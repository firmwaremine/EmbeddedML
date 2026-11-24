"""Offline compatibility/integrity gate. Intentionally NOT a signature verifier."""
from pathlib import Path
import hashlib,json,copy
D=Path(__file__).resolve().parent;E=D.parent
model=E/'neural/generated/neural_model.json'
manifest={'schema':1,'artifact':'neural/generated/neural_model.json','sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'family':'teaching-3-8-3','input_features':3,'preprocessing':'mean-acrms-mad-v1','labels':['idle','smooth','rough'],'revision':2,'verification':'host-replay-only','signature_verified':False}
def gate(m,payload,current_revision=1):
 if m.get('schema')!=1 or m.get('family')!='teaching-3-8-3' or m.get('input_features')!=3:return False
 if m.get('preprocessing')!='mean-acrms-mad-v1' or m.get('labels')!=['idle','smooth','rough']:return False
 if type(m.get('revision')) is not int or m['revision']<=current_revision:return False
 return hashlib.sha256(payload).hexdigest()==m.get('sha256')
payload=model.read_bytes();assert gate(manifest,payload)
assert not gate(manifest,payload+b' ')
for field,value in [('schema',2),('family','other'),('input_features',4),('preprocessing','different'),('labels',['rough','smooth','idle']),('revision',1)]:
 bad=copy.deepcopy(manifest);bad[field]=value;assert not gate(bad,payload)
(D/'release_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
out={'status':'PASS','accepted_fixture':1,'rejected_tamper_or_incompatibility_fixtures':7,'authentication':'NOT implemented; anyone able to replace both manifest and payload can recompute hash','activation':'NOT implemented; no files flashed or active state changed'}
(D/'release_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
