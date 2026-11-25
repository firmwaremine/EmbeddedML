from pathlib import Path
import torch,torchvision,numpy as np,json,operator,math
R=Path(__file__).resolve().parent;O=R/'c_vision';O.mkdir(exist_ok=True);torch.set_num_threads(1)
saved=torch.load(R/'flower_model.pt',weights_only=True);m=torchvision.models.mobilenet_v3_small(weights=None);m.classifier=torch.nn.Identity();m.load_state_dict(saved['backbone']);m.eval();head=torch.nn.Linear(576,5);head.load_state_dict(saved['head']);head.eval();model=torch.nn.Sequential(m,head).eval();graph=torch.fx.symbolic_trace(model);mods=dict(graph.named_modules())
class Capture(torch.fx.Interpreter):
 def __init__(self,g):super().__init__(g);self.values={}
 def run_node(self,n):
  v=super().run_node(n)
  if isinstance(v,torch.Tensor):self.values[n]=v.detach().clone()
  return v
cap=Capture(graph);cap.run(torch.zeros(1,3,96,96));nodes=[n for n in graph.graph.nodes if n.op!='output'];index={n:i for i,n in enumerate(nodes)}
# Static lifetime allocation: release only after a node's last consumer. Float units.
last={n:max([index[u] for u in n.users if u in index] or [len(nodes)]) for n in nodes};active=[];free=[];offset={};peak=0;size={n:cap.values[n].numel() for n in nodes}
for i,n in enumerate(nodes):
 for old in active[:]:
  if last[old]<i:free.append((offset[old],size[old]));active.remove(old)
 free.sort();merged=[]
 for start,length in free:
  if merged and merged[-1][0]+merged[-1][1]==start:merged[-1]=(merged[-1][0],merged[-1][1]+length)
  else:merged.append((start,length))
 free=merged;candidate=next((j for j,x in enumerate(free) if x[1]>=size[n]),None)
 if candidate is None:offset[n]=peak;peak+=size[n]
 else:
  start,length=free.pop(candidate);offset[n]=start
  if length>size[n]:free.append((start+size[n],length-size[n]))
 active.append(n)
weights=[]
def add(v):
 a=v.detach().cpu().numpy().astype('float32').ravel();start=sum(len(x) for x in weights);weights.append(a);return 'w+'+str(start)
def ptr(n):return 'a+'+str(offset[n])
code=['#include "vision_c.h"','#include <math.h>','#include <string.h>', '''static void conv(const float*x,float*y,const float*w,const float*b,int ci,int hi,int wi,int co,int ho,int wo,int kh,int kw,int sh,int sw,int ph,int pw,int groups){
 int ig=ci/groups,og=co/groups;
 for(int oc=0;oc<co;oc++)for(int oy=0;oy<ho;oy++)for(int ox=0;ox<wo;ox++){
  float sum=b?b[oc]:0;int group=oc/og;
  for(int ic=0;ic<ig;ic++)for(int ky=0;ky<kh;ky++){int iy=oy*sh+ky-ph;if(iy<0||iy>=hi)continue;
   for(int kx=0;kx<kw;kx++){int ix=ox*sw+kx-pw;if(ix>=0&&ix<wi)sum+=x[((group*ig+ic)*hi+iy)*wi+ix]*w[((oc*ig+ic)*kh+ky)*kw+kx];}}
  y[(oc*ho+oy)*wo+ox]=sum;
 }
}
static void bn(const float*x,float*y,const float*s,const float*b,int c,int spatial){for(int j=0;j<c;j++)for(int k=0;k<spatial;k++)y[j*spatial+k]=x[j*spatial+k]*s[j]+b[j];}
static void act(const float*x,float*y,int n,int type){for(int i=0;i<n;i++){float v=x[i];if(type==0)y[i]=fmaxf(v,0);else if(type==1)y[i]=v*fminf(fmaxf(v+3,0),6)/6;else y[i]=fminf(fmaxf(v+3,0),6)/6;}}
static void gap(const float*x,float*y,int c,int n){for(int j=0;j<c;j++){float sum=0;for(int i=0;i<n;i++)sum+=x[j*n+i];y[j]=sum/n;}}
static void dense(const float*x,float*y,const float*w,const float*b,int ni,int no){for(int o=0;o<no;o++){float sum=b[o];for(int i=0;i<ni;i++)sum+=x[i]*w[o*ni+i];y[o]=sum;}}
''','int vision_run(const float *input,const float *w,float *a,float *output,vision_observer observer){']
ledger=[]
for n in nodes:
 i=index[n];shape=list(cap.values[n].shape);args=[x for x in n.args if isinstance(x,torch.fx.Node)];x=ptr(args[0]) if args else None;y=ptr(n);count=size[n];op=''
 if n.op=='placeholder':op=f'memcpy({y},input,{count}*sizeof(float));'
 elif n.op=='call_module':
  module=mods[n.target]
  if isinstance(module,torch.nn.Conv2d):
   si=cap.values[args[0]].shape;_,co,ho,wo=shape;_,ci,hi,wi=si;kh,kw=module.kernel_size;sh,sw=module.stride;ph,pw=module.padding;ww=add(module.weight);bb=add(module.bias) if module.bias is not None else '0';op=f'conv({x},{y},{ww},{bb},{ci},{hi},{wi},{co},{ho},{wo},{kh},{kw},{sh},{sw},{ph},{pw},{module.groups});'
  elif isinstance(module,torch.nn.BatchNorm2d):
   scale=module.weight/torch.sqrt(module.running_var+module.eps);bias=module.bias-module.running_mean*scale;ss=add(scale);bb=add(bias);op=f'bn({x},{y},{ss},{bb},{shape[1]},{count//shape[1]});'
  elif isinstance(module,(torch.nn.ReLU,torch.nn.Hardswish,torch.nn.Hardsigmoid)):
   typ=0 if isinstance(module,torch.nn.ReLU) else 1 if isinstance(module,torch.nn.Hardswish) else 2;op=f'act({x},{y},{count},{typ});'
  elif isinstance(module,torch.nn.AdaptiveAvgPool2d):op=f'gap({x},{y},{shape[1]},{size[args[0]]//shape[1]});'
  elif isinstance(module,torch.nn.Linear):ww=add(module.weight);bb=add(module.bias);op=f'dense({x},{y},{ww},{bb},{module.in_features},{module.out_features});'
  elif isinstance(module,torch.nn.Identity):op=f'memcpy({y},{x},{count}*sizeof(float));'
  else:raise ValueError(module)
 elif n.op=='call_function':
  if n.target==operator.add:op=f'for(int i=0;i<{count};i++)a[{offset[n]}+i]=a[{offset[args[0]]}+i]+a[{offset[args[1]]}+i];'
  elif n.target==operator.mul:
   p,q=args;small,big=(p,q) if size[p]<size[q] else (q,p);spatial=size[big]//size[small];op=f'for(int i=0;i<{count};i++)a[{offset[n]}+i]=a[{offset[big]}+i]*a[{offset[small]}+i/{spatial}];'
  elif n.target==torch.flatten:op=f'memcpy({y},{x},{count}*sizeof(float));'
  else:raise ValueError(n.target)
 else:raise ValueError(n.op)
 code.append(op+f'\nif(observer)observer({i},{y},{count});');ledger.append(dict(index=i,name=n.name,operation=str(n.target),shape=shape,arena_float_offset=offset[n],floats=count))
final=nodes[-1];code.append(f'memcpy(output,{ptr(final)},5*sizeof(float));int best=0;for(int i=1;i<5;i++)if(output[i]>output[best])best=i;return best;}}')
(O/'vision_c.c').write_text('\n'.join(code));(O/'vision_c.h').write_text(f'''#ifndef VISION_C_H
#define VISION_C_H
/* Fixed 96x96 NCHW normalized float input. No runtime allocation. Not reentrant with a shared arena. */
#define VISION_ARENA_FLOATS {peak}
#define VISION_INPUT_FLOATS 27648
typedef void (*vision_observer)(int layer,const float *values,int count);
int vision_run(const float*input,const float*weights,float*arena,float*output,vision_observer observer);
#endif
''');np.concatenate(weights).tofile(O/'weights.f32');(O/'layers.json').write_text(json.dumps(ledger,indent=2));print('nodes',len(nodes),'arena',peak*4,'weights',sum(len(x) for x in weights)*4)
torch.save(graph,O/'reference_graph.pt')
