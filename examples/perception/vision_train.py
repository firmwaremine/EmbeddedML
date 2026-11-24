"""Original tiny spatial-color teaching dataset. Not a camera recognition model."""
from pathlib import Path
import random,json,math,struct
D=Path(__file__).resolve().parent
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def image(session,label,repeat):
 r=random.Random(70013+session*1000+label*100+repeat);brightness=r.uniform(.55,1.0);p=[]
 for y in range(16):
  for x in range(16):
   # Classes: red-left, red-right, gray. Vary brightness and pixel noise.
   base=([200,35,35] if (x<8)==(label==0) else [35,35,200]) if label<2 else [105,105,105]
   p.extend(max(0,min(255,round(v*brightness+r.gauss(0,8)))) for v in base)
 return p
def features(p):return [f32(sum(p[(y*16+x)*3+c] for y in range(16) for x in range(half*8,(half+1)*8))/(128*255)) for half in range(2) for c in range(3)]
def data():
 for s in range(30):
  for l in range(3):
   for r in range(10):yield s,l,r,image(s,l,r)
def predict(f,m):
 d=[sum(((f[i]-m['mean'][i])/m['scale'][i]-c[i])**2 for i in range(6)) for c in m['centers']]
 return min(range(3),key=d.__getitem__),d
if __name__=='__main__':
 tr=[(l,features(p)) for s,l,r,p in data() if s<18]
 mean=[f32(sum(f[i] for l,f in tr)/len(tr)) for i in range(6)]
 scale=[f32(math.sqrt(sum((f[i]-mean[i])**2 for l,f in tr)/len(tr))) for i in range(6)]
 centers=[[f32(sum((f[i]-mean[i])/scale[i] for ll,f in tr if ll==l)/sum(ll==l for ll,f in tr)) for i in range(6)] for l in range(3)]
 m={'mean':mean,'scale':scale,'centers':centers,'labels':['red_left','red_right','gray'],'seed':'70013 + session*1000 + label*100 + repeat'}
 (D/'vision_model.json').write_text(json.dumps(m,indent=2)+'\n')
 def arr(v):return '{'+','.join(arr(x) if isinstance(x,list) else f'{x:.9e}f' for x in v)+'}'
 (D/'vision_model.h').write_text('#ifndef VISION_MODEL_H\n#define VISION_MODEL_H\n'+''.join('static const float vision_'+k+('[3][6]' if k=='centers' else '[6]')+' = '+arr(m[k])+';\n' for k in ['mean','scale','centers'])+'#endif\n')
 report={}
 for name,lo,hi in [('train',0,18),('validation',18,24),('test',24,30)]:
  cm=[[0]*3 for _ in range(3)]
  for s,l,r,p in data():
   if lo<=s<hi:cm[l][predict(features(p),m)[0]]+=1
  report[name]={'windows':sum(map(sum,cm)),'confusion':cm}
 (D/'vision_training_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
