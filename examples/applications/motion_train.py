"""Original synthetic motion-pattern lab. No human recordings, no field claim."""
from pathlib import Path
import json, math, random, struct
D=Path(__file__).resolve().parent
LABELS=['quiet','sway','vibrate']
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def samples(person,session,label,repeat):
    r=random.Random(13001+person*1000+session*100+label*10+repeat)
    # One rigid coordinate rotation for the whole window, applied to gravity too.
    a=r.uniform(-math.pi,math.pi);b=r.uniform(-1,1);phase=r.uniform(0,2*math.pi)
    amp=[.003,.12,.18][label]*(1+r.uniform(-.15,.15))
    hz=[0,1.5,8][label]*(1+r.uniform(-.1,.1))
    out=[]
    for n in range(64):
        x=.008*math.sin(.17*n+phase)+r.gauss(0,.001)
        y=.005*math.cos(.11*n+phase)+r.gauss(0,.001)
        z=1+amp*math.sin(2*math.pi*hz*n/50+phase)+r.gauss(0,.001)
        xx=x*math.cos(a)-y*math.sin(a);yy=x*math.sin(a)+y*math.cos(a)
        out.append([f32(xx*math.cos(b)+z*math.sin(b)),f32(yy),f32(-xx*math.sin(b)+z*math.cos(b))])
    return out

def features(x):
    m=[math.hypot(*p) for p in x];mean=sum(m)/64
    return [mean,math.sqrt(sum((v-mean)**2 for v in m)/64),sum(abs(m[i]-m[i-1]) for i in range(1,64))/63]
def dataset():
    for person in range(20):
      for session in range(3):
       for label in range(3):
        for repeat in range(6):
         yield person,session,label,repeat,samples(person,session,label,repeat)
def classify(f,m):
    z=[(f[i]-m['mean'][i])/m['scale'][i] for i in range(3)]
    d=[sum((z[i]-c[i])**2 for i in range(3)) for c in m['centers']]
    return min(range(3),key=d.__getitem__),d

def train():
    data=list(dataset());train=[(l,features(x)) for p,s,l,r,x in data if p<12]
    mean=[sum(f[i] for l,f in train)/len(train) for i in range(3)]
    scale=[math.sqrt(sum((f[i]-mean[i])**2 for l,f in train)/len(train)) for i in range(3)]
    centers=[[sum((f[i]-mean[i])/scale[i] for ll,f in train if ll==l)/sum(ll==l for ll,f in train) for i in range(3)] for l in range(3)]
    # Export values rounded exactly to C float before computing reported results.
    m={'mean':list(map(f32,mean)),'scale':list(map(f32,scale)),'centers':[list(map(f32,c)) for c in centers],'labels':LABELS,'n':64,'sample_rate_hz':50,'units':'g','generator':'13001 + person*1000 + session*100 + label*10 + repeat'}
    (D/'motion_model.json').write_text(json.dumps(m,indent=2)+'\n')
    def arr(v):return '{'+','.join(arr(x) if isinstance(x,list) else f'{x:.9e}f' for x in v)+'}'
    (D/'motion_model.h').write_text('#ifndef MOTION_MODEL_H\n#define MOTION_MODEL_H\n'+''.join('static const float motion_'+k+('[3][3]' if k=='centers' else '[3]')+' = '+arr(m[k])+';\n' for k in ['mean','scale','centers'])+'#endif\n')
    result={}
    for name,lo,hi in [('train',0,12),('validation',12,16),('test',16,20)]:
      cm=[[0]*3 for _ in range(3)]
      for p,s,l,r,x in data:
       if lo<=p<hi:cm[l][classify(list(map(f32,features(x))),m)[0]]+=1
      result[name]={'windows':sum(map(sum,cm)),'confusion':cm}
    (D/'motion_training_report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':train()
