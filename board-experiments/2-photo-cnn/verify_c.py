from pathlib import Path
import json,ctypes,time,hashlib
import numpy as np,torch,torchvision
from PIL import Image,ImageOps
R=Path(__file__).resolve().parent;O=R/'c_vision';torch.set_num_threads(1);s=torch.load(R/'flower_model.pt',weights_only=True);m=torchvision.models.mobilenet_v3_small(weights=None);m.classifier=torch.nn.Identity();m.load_state_dict(s['backbone']);head=torch.nn.Linear(576,5);head.load_state_dict(s['head']);model=torch.nn.Sequential(m,head).eval();g=torch.fx.symbolic_trace(model)
class Capture(torch.fx.Interpreter):
 def __init__(self,g):super().__init__(g);self.values=[]
 def run_node(self,n):
  v=super().run_node(n)
  if n.op!='output':self.values.append(v.detach().numpy().ravel().copy())
  return v
lib=ctypes.CDLL(str(O/'libvision.so'));fp=np.ctypeslib.ndpointer(dtype=np.float32,flags='C_CONTIGUOUS');CB=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.POINTER(ctypes.c_float),ctypes.c_int);lib.vision_run.argtypes=[fp,fp,fp,fp,CB];lib.vision_run.restype=ctypes.c_int
ledger=json.loads((O/'layers.json').read_text());arena=np.zeros(max(x['arena_float_offset']+x['floats'] for x in ledger),np.float32);weights=np.fromfile(O/'weights.f32',np.float32);out=np.zeros(5,np.float32);manifest=json.loads((R/'split_manifest.json').read_text());test=[x for x in manifest if x['split']==2];mean=np.array([.485,.456,.406],np.float32)[:,None,None];std=np.array([.229,.224,.225],np.float32)[:,None,None];layer_errors=np.zeros(len(ledger));max_logit_error=0.0;matches=0;times=[];predictions=[];reference=[]
for i,row in enumerate(test):
 p=R.parents[1]/'realdata/data/flower_photos'/row['path'];im=ImageOps.fit(Image.open(p).convert('RGB'),(96,96),method=Image.Resampling.BILINEAR);x=((np.asarray(im,dtype=np.float32).transpose(2,0,1)/255-mean)/std).copy();cap=Capture(g)
 with torch.no_grad():expected=cap.run(torch.tensor(x[None])).numpy().ravel()
 def observe(layer,ptr,n):
  actual=np.ctypeslib.as_array(ptr,shape=(n,));layer_errors[layer]=max(layer_errors[layer],float(np.max(np.abs(actual-cap.values[layer]))))
 cb=CB(observe);t=time.perf_counter();pred=lib.vision_run(x.ravel(),weights,arena,out,cb);times.append((time.perf_counter()-t)*1000);max_logit_error=max(max_logit_error,float(np.max(np.abs(out-expected))));matches+=pred==expected.argmax();predictions.append(int(pred));reference.append(int(expected.argmax()))
 if i==0:x.tofile(O/'replay_input.f32');expected.tofile(O/'replay_logits.f32')
 if i%100==0:print(i,'agreement',matches,'max layer',layer_errors.max(),flush=True)
labels=json.loads((R/'report.json').read_text())['labels'];truth=[labels.index(x['path'].split('/')[0]) for x in test];cm=np.zeros((5,5),int)
for a,b in zip(truth,predictions):cm[a,b]+=1
report=dict(images=len(test),labels_agree=int(matches),max_observed_layer_abs_error=float(layer_errors.max()),layer_check_images=len(test),max_output_logit_abs_error=max_logit_error,layers=[dict(name=x['name'],max_abs_error=float(e)) for x,e in zip(ledger,layer_errors)],c_test_accuracy=float(cm.trace()/cm.sum()),c_confusion_matrix=cm.tolist(),arena_bytes=arena.nbytes,weights_bytes=weights.nbytes,host_ms=dict(median=float(np.median(times)),p95=float(np.percentile(times,95)),maximum=float(max(times))),scope='Strict C11 host reference. Input crop/resize performed by Pillow, not claimed as a camera adapter. 555-image all-layer and output-label check. No Korvo execution or optimized timing.')
(O/'parity_report.json').write_text(json.dumps(report,indent=2));assert matches==len(test),report;assert layer_errors.max()<.01,layer_errors.max();assert max_logit_error<.01,max_logit_error;print({k:v for k,v in report.items() if k!='layers'})
