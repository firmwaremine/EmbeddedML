#!/usr/bin/env python3
"""Original 3-8-3 MLP and power-of-two integer teaching deployment.
Requires NumPy. Does NOT generate a LiteRT or ESP-DL model.
"""
import json, math, sys, hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import train
OUT=Path(__file__).resolve().parent/'generated';OUT.mkdir(exist_ok=True)

def away(x): return np.copysign(np.floor(np.abs(x)+0.5),x).astype(np.int64)
def exponent(maximum):
    return int(math.ceil(math.log2(max(float(maximum),1e-9)/127)))
def quant(x,e): return np.clip(away(x/(2.**e)),-128,127)
def shift(v,e):
    v=int(v)
    if e>=0:return v*(1<<e)
    divisor=1<<(-e)
    return (1 if v>=0 else -1)*((abs(v)+divisor//2)//divisor)
def qinfer(z,q):
    x=quant(np.asarray(z),q['ex']).astype(np.int64)
    h=[];sat=0
    for j in range(8):
        a=int(q['b1'][j])+sum(int(x[i])*int(q['w1'][i][j]) for i in range(3))
        assert -(2**31)<=a<2**31
        r=max(0,shift(a,q['ex']+q['ew1']-q['eh']))
        sat+=int(r>127);h.append(min(127,r))
    logits=[]
    for k in range(3):
        a=int(q['b2'][k])+sum(h[j]*int(q['w2'][j][k]) for j in range(8))
        assert -(2**31)<=a<2**31;logits.append(a)
    return int(np.argmax(logits)),logits,h,sat

def main():
    rows=train.load_csv(ROOT/'data/windows.csv')
    f=np.array([train.features(r['raw']) for r in rows],dtype=np.float64)
    y=np.array([r['label'] for r in rows]);masks={s:np.array([r['split']==s for r in rows]) for s in ['train','validation','test']}
    mu=f[masks['train']].mean(0);scale=np.maximum(f[masks['train']].std(0),1e-6)
    z=(f-mu)/scale;xt=z[masks['train']];yt=y[masks['train']]
    rng=np.random.default_rng(27491)
    w1=rng.normal(0,0.3,(3,8));b1=np.zeros(8);w2=rng.normal(0,0.3,(8,3));b2=np.zeros(3)
    history=[];best=None;bestloss=float('inf')
    # Full-batch gradient descent. Selection uses validation only.
    for epoch in range(1200):
        pre=xt@w1+b1;h=np.maximum(pre,0);logits=h@w2+b2
        p=np.exp(logits-logits.max(1,keepdims=True));p/=p.sum(1,keepdims=True)
        grad=p.copy();grad[np.arange(len(yt)),yt]-=1;grad/=len(yt)
        dw2=h.T@grad;db2=grad.sum(0)
        dh=(grad@w2.T)*(pre>0);dw1=xt.T@dh;db1=dh.sum(0)
        lr=.04
        w1-=lr*dw1;b1-=lr*db1;w2-=lr*dw2;b2-=lr*db2
        if epoch%10==0 or epoch==1199:
            xv=z[masks['validation']];yv=y[masks['validation']]
            vl=np.maximum(xv@w1+b1,0)@w2+b2
            lp=vl-vl.max(1,keepdims=True);loss=float(np.mean(np.log(np.exp(lp).sum(1))-lp[np.arange(len(yv)),yv]))
            tr=float(-np.log(np.maximum(p[np.arange(len(yt)),yt],1e-300)).mean())
            history.append(dict(epoch=epoch+1,training_loss_before_update=tr,validation_loss_after_update=loss))
            if loss<bestloss:bestloss=loss;best=tuple(v.copy() for v in [w1,b1,w2,b2]);selected=epoch+1
    w1,b1,w2,b2=best
    hidden=np.maximum(xt@w1+b1,0)
    ex=exponent(abs(xt).max());ew1=exponent(abs(w1).max());eh=exponent(hidden.max());ew2=exponent(abs(w2).max())
    qw1=quant(w1,ew1);qw2=quant(w2,ew2)
    qb1=away(b1/(2.**(ex+ew1)));qb2=away(b2/(2.**(eh+ew2)))
    q=dict(ex=ex,ew1=ew1,eh=eh,ew2=ew2,w1=qw1.tolist(),b1=qb1.tolist(),w2=qw2.tolist(),b2=qb2.tolist())
    bounds1=(3*128*128+np.abs(qb1)).astype(np.int64)
    bounds2=(8*127*128+np.abs(qb2)).astype(np.int64)
    assert max(bounds1.max(),bounds2.max())<2**31
    result={};sat=0
    for split,mask in masks.items():
        logits=np.maximum(z[mask]@w1+b1,0)@w2+b2;fp=logits.argmax(1)
        qp=[]
        for zz in z[mask]:
            pred,_,_,ss=qinfer(zz,q);qp.append(pred);sat+=ss
        cm=np.zeros((3,3),dtype=int)
        for actual,pred in zip(y[mask],qp):cm[actual,pred]+=1
        result[split]=dict(n=int(mask.sum()),float_accuracy=float(np.mean(fp==y[mask])),
            integer_accuracy=float(np.mean(np.array(qp)==y[mask])),float_integer_agreement=float(np.mean(fp==np.array(qp))),confusion_integer=cm.tolist())
    model=dict(mean=mu.tolist(),scale=scale.tolist(),w1=w1.tolist(),b1=b1.tolist(),w2=w2.tolist(),b2=b2.tolist(),quant=q)
    (OUT/'neural_model.json').write_text(json.dumps(model,indent=2)+'\n')
    report=dict(seed=27491,numpy_version=np.__version__,selected_epoch=selected,selection='minimum sampled validation loss; test not used',
        architecture=[3,8,3],activation='ReLU',loss='multiclass cross entropy',optimizer='full-batch gradient descent',learning_rate=.04,
        quantization='original per-tensor power-of-two static teaching format; not LiteRT/ESP-DL',calibration='training features and hidden activations only',
        accumulator_bound_layer1=int(bounds1.max()),accumulator_bound_layer2=int(bounds2.max()),hidden_saturation_events_all_rows=sat,
        reports=result,history=history,sha256=hashlib.sha256((OUT/'neural_model.json').read_bytes()).hexdigest())
    (OUT/'training_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='history'},indent=2))
if __name__=='__main__':main()
