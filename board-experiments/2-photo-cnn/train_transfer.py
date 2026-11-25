from pathlib import Path
import torch,torchvision,numpy as np,json,hashlib,time,platform
from PIL import Image,ImageOps
R=Path(__file__).resolve().parent;D=R.parent/'data/flower_photos';torch.set_num_threads(1);torch.manual_seed(20261124);np.random.seed(20261124)
labels=sorted(p.name for p in D.iterdir() if p.is_dir());weights=torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1;model=torchvision.models.mobilenet_v3_small(weights=weights);model.classifier=torch.nn.Identity();model.eval()
files=sorted(D.glob('*/*.jpg'));mean=np.array([.485,.456,.406],np.float32)[:,None,None];std=np.array([.229,.224,.225],np.float32)[:,None,None];manifest=[];start=time.perf_counter()
if not (R/'embeddings.npz').exists():
 features=[]
 for base in range(0,len(files),32):
  batch=[]
  for p in files[base:base+32]:
   im=ImageOps.fit(Image.open(p).convert('RGB'),(96,96),method=Image.Resampling.BILINEAR);arr=np.asarray(im,dtype=np.float32).transpose(2,0,1)/255;batch.append((arr-mean)/std)
  with torch.no_grad():f=model(torch.tensor(np.array(batch))).numpy()
  features.append(f)
  print('embedded',base+len(batch),flush=True)
 np.savez_compressed(R/'embeddings.npz',X=np.concatenate(features))
X=np.load(R/'embeddings.npz')['X'];Y=[];S=[]
for p in files:
 digest=hashlib.sha256(p.read_bytes()).hexdigest();v=int(digest[:8],16)%100;split=0 if v<70 else 1 if v<85 else 2;Y.append(labels.index(p.parent.name));S.append(split);manifest.append(dict(path=str(p.relative_to(D)),sha256=digest,split=split))
Y=np.array(Y);S=np.array(S);head=torch.nn.Linear(X.shape[1],5);opt=torch.optim.Adam(head.parameters(),lr=.005,weight_decay=.001);xt=torch.tensor(X[S==0]);yt=torch.tensor(Y[S==0]);xv=torch.tensor(X[S==1]);yv=torch.tensor(Y[S==1]);best=1e9;history=[]
for epoch in range(100):
 perm=torch.randperm(len(xt));total=0
 for ids in perm.split(128):
  opt.zero_grad();loss=torch.nn.functional.cross_entropy(head(xt[ids]),yt[ids]);loss.backward();opt.step();total+=loss.item()*len(ids)
 with torch.no_grad():v=torch.nn.functional.cross_entropy(head(xv),yv).item();acc=(head(xv).argmax(1)==yv).float().mean().item()
 history.append(dict(epoch=epoch+1,train_loss=total/len(xt),validation_loss=v,validation_accuracy=acc))
 if v<best:best=v;torch.save(head.state_dict(),R/'head.pt')
head.load_state_dict(torch.load(R/'head.pt',weights_only=True))
with torch.no_grad():logits=head(torch.tensor(X[S==2])).numpy()
pred=logits.argmax(1);truth=Y[S==2];cm=np.zeros((5,5),int)
for y,p in zip(truth,pred):cm[y,p]+=1
report=dict(labels=labels,counts={k:int((S==i).sum()) for i,k in enumerate(['train','validation','test'])},test_accuracy=float((pred==truth).mean()),confusion_matrix=cm.tolist(),backbone='torchvision MobileNetV3-Small IMAGENET1K_V1, frozen',input='96x96 RGB center-square bilinear crop; /255 then ImageNet channel mean/std',split='sha256(file bytes) first32bits mod100; <70 train,<85 validation,else test; exact duplicates group together; near-duplicates/session provenance not guaranteed',scope='Host real-photo transfer learning. NOT a Korvo C deployment, object detector, camera test or field benchmark.',torch=torch.__version__,torchvision=torchvision.__version__,elapsed_seconds=time.perf_counter()-start,history=history)
(R/'report.json').write_text(json.dumps(report,indent=2));(R/'split_manifest.json').write_text(json.dumps(manifest,indent=2));torch.save(dict(backbone=model.state_dict(),head=head.state_dict()),R/'flower_model.pt');print(json.dumps({k:v for k,v in report.items() if k!='history'},indent=2))
