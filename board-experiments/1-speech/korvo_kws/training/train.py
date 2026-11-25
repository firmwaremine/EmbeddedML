from pathlib import Path
import hashlib,json,wave,time,platform
import numpy as np
from scipy import signal
import torch
R=Path(__file__).resolve().parent;D=R.parent/'data/mini_speech_commands';torch.set_num_threads(1);torch.manual_seed(20261124);np.random.seed(20261124)
labels=['go','no','stop','yes','other'];rate=16000;fft=512;frame=400;hop=320;bands=24
# HTK mel conversion, triangular weights on the discrete rFFT bins, no area normalization.
mel=lambda f:2595*np.log10(1+f/700)
hz=lambda m:700*(10**(m/2595)-1)
edges=hz(np.linspace(mel(80),mel(7600),bands+2));freq=np.arange(257)*rate/fft
bank=np.maximum(0,np.minimum((freq[None,:]-edges[:-2,None])/(edges[1:-1,None]-edges[:-2,None]),(edges[2:,None]-freq[None,:])/(edges[2:,None]-edges[1:-1,None]))).astype('float32');win=np.hanning(frame+1)[:-1].astype('float32')
def features(pcm):
 x=np.zeros(16000,np.float32);x[:min(len(pcm),16000)]=pcm[:16000].astype(np.float32)/32768
 frames=np.lib.stride_tricks.sliding_window_view(x,frame)[::hop][:49]*win
 power=(np.abs(np.fft.rfft(frames,n=fft,axis=1))**2).astype('float32')
 return np.log(np.maximum(power@bank.T,1e-8)).astype('float32').reshape(-1)
if not (R/'features.npz').exists():
 X=[];Y=[];S=[];paths=[];speakers=[]
 for p in sorted(D.glob('*/*.wav')):
  with wave.open(str(p)) as w:
   assert w.getframerate()==16000 and w.getnchannels()==1 and w.getsampwidth()==2
   pcm=np.frombuffer(w.readframes(w.getnframes()),'<i2')
  speaker=p.stem.split('_nohash_')[0];v=int(hashlib.sha256(speaker.encode()).hexdigest()[:8],16)%100;split=0 if v<70 else 1 if v<85 else 2
  X.append(features(pcm));Y.append(labels.index(p.parent.name) if p.parent.name in labels else 4);S.append(split);paths.append(str(p.relative_to(D)));speakers.append(speaker)
 np.savez_compressed(R/'features.npz',X=np.array(X),Y=Y,S=S)
 (R/'split_manifest.json').write_text(json.dumps(dict(seed=20261124,rule='sha256(speaker) first32bits mod100: <70 train, <85 validation, else test',files=[dict(path=p,speaker=s,split=int(k)) for p,s,k in zip(paths,speakers,S)]),indent=2))
z=np.load(R/'features.npz');baseX=z['X'];Y=z['Y'];S=z['S']
if not (R/'augmented.npz').exists():
 rng=np.random.default_rng(20261124);augX=[baseX[S==0]];augY=[Y[S==0]]
 rows=json.loads((R/'split_manifest.json').read_text())['files'];extra=[];extraY=[]
 for row,y in zip(rows,Y):
  if row['split']!=0:continue
  with wave.open(str(D/row['path'])) as w:raw=np.frombuffer(w.readframes(w.getnframes()),'<i2')
  source=np.zeros(16000,np.int16);source[:len(raw)]=raw
  for shift in [-4800,-2400,2400,4800]:
   out=np.zeros(16000,np.int16)
   if shift>0:out[shift:]=source[:-shift]
   else:out[:shift]=source[-shift:]
   extra.append(features(out));extraY.append(y)
 for _ in range(1500):
  level=rng.uniform(0,.008);noise=np.clip(rng.normal(0,level,16000)*32768,-32768,32767).astype(np.int16)
  extra.append(features(noise));extraY.append(4)
 augX.append(np.asarray(extra));augY.append(np.asarray(extraY));np.savez_compressed(R/'augmented.npz',X=np.concatenate(augX),Y=np.concatenate(augY))
aug=np.load(R/'augmented.npz');mean=aug['X'].mean(0);std=np.maximum(aug['X'].std(0),.5);trainX=(aug['X']-mean)/std;trainY=aug['Y'];X=(baseX-mean)/std
model=torch.nn.Sequential(torch.nn.Linear(1176,64),torch.nn.ReLU(),torch.nn.Linear(64,5));opt=torch.optim.Adam(model.parameters(),lr=.001,weight_decay=.0001);xt=torch.tensor(trainX);yt=torch.tensor(trainY);xv=torch.tensor(X[S==1]);yv=torch.tensor(Y[S==1]);best=1e9;history=[];t=time.perf_counter()
for epoch in range(50):
 model.train();perm=torch.randperm(len(xt));loss_sum=0
 for ids in perm.split(128):
  opt.zero_grad();out=model(xt[ids]);loss=torch.nn.functional.cross_entropy(out,yt[ids]);loss.backward();opt.step();loss_sum+=loss.item()*len(ids)
 model.eval()
 with torch.no_grad():v=torch.nn.functional.cross_entropy(model(xv),yv).item();acc=(model(xv).argmax(1)==yv).float().mean().item()
 history.append(dict(epoch=epoch+1,train_loss=loss_sum/len(xt),val_loss=v,val_accuracy=acc))
 if v<best:best=v;torch.save(model.state_dict(),R/'model.pt')
 print(epoch+1,round(v,4),round(acc,4),flush=True)
model.load_state_dict(torch.load(R/'model.pt',weights_only=True));model.eval()
with torch.no_grad():logits=model(torch.tensor(X[S==2])).numpy()
pred=logits.argmax(1);truth=Y[S==2];cm=np.zeros((5,5),int)
for y,p in zip(truth,pred):cm[y,p]+=1
np.savez(R/'model.npz',w1=model[0].weight.detach().numpy(),b1=model[0].bias.detach().numpy(),w2=model[2].weight.detach().numpy(),b2=model[2].bias.detach().numpy(),mean=mean,std=std,bank=bank,window=win)
report=dict(augmentation="Training speakers only: shifts +/-150ms, +/-300ms plus 1500 synthetic quiet/noise negatives mapped to other. Test clips are real and unshifted.",labels=labels,counts={k:int((S==v).sum()) for v,k in enumerate(['train','validation','test'])},test_accuracy=float((pred==truth).mean()),confusion_matrix=cm.tolist(),test_support=cm.sum(1).tolist(),history=history,training_seconds=time.perf_counter()-t,torch=torch.__version__,python=platform.python_version(),platform=platform.platform(),scope='Real public recorded clips, speaker-disjoint custom split. Other means only down/left/right/up. No arbitrary-speech/noise rejection or physical Korvo result.',frontend=dict(rate=rate,frame=frame,hop=hop,fft=fft,bands=bands,frames=49,range_hz=[80,7600],log_floor=1e-8,normalization='train-only per-feature mean/std, std floor 0.5'))
(R/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='history'},indent=2))
