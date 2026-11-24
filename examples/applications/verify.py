"""Independent NumPy spectrum oracle; synthetic motion parity, rotations and faults."""
from pathlib import Path
import json,math,subprocess,sys
import numpy as np
from motion_train import dataset,features,classify,f32
D=Path(__file__).resolve().parent;exe=str(Path(sys.argv[1]).resolve())
m=json.loads((D/'motion_model.json').read_text())
def run(mode,values,valid=True):
 p=subprocess.run([exe,mode],input=' '.join(map(str,values))+'\n',text=True,capture_output=True)
 if not valid:assert p.returncode==2,(p.returncode,p.stderr);return
 assert p.returncode==0,p.stderr
 return json.loads(p.stdout)
maxf=0.;maxd=0.;known={};count=0
for person,session,label,repeat,x in dataset():
 y=run('motion',[v for row in x for v in row]);f=list(map(f32,features(x)));pred,d=classify(f,m)
 assert y['label']==pred
 maxf=max(maxf,max(abs(a-b) for a,b in zip(y['features'],f)))
 maxd=max(maxd,max(abs(a-b) for a,b in zip(y['distances'],d)))
 assert np.allclose(y['features'],f,rtol=2e-6,atol=2e-7)
 assert np.allclose(y['distances'],d,rtol=3e-6,atol=3e-6)
 if person==0 and session==0 and repeat==0:known[m['labels'][label]]=y
 count+=1
# Exact orthogonal coordinate permutation/sign change, same vector norm.
x=next(dataset())[-1];rot=[[v[2],-v[0],v[1]] for v in x]
a=run('motion',[v for row in x for v in row]);b=run('motion',[v for row in rot for v in row]);assert np.allclose(a['features'],b['features'],rtol=0,atol=1e-7)
for val in [float('nan'),float('inf'),16.1]:
 bad=[0.]*192;bad[0]=val;run('motion',bad,False)
run('motion',[0.]*191,False);run('motion',[0.]*193,False)
N=256;n=np.arange(N);fixtures={
'silence':np.zeros(N,dtype=np.int16),
'dc':np.full(N,1234,dtype=np.int16),
'bin16':np.rint(12000*np.sin(2*np.pi*16*n/N)).astype(np.int16),
'impulse':np.array([30000]+[0]*255,dtype=np.int16),
'fullscale':np.array([-32768,32767]*128,dtype=np.int16),
'noise':np.random.default_rng(49271).integers(-15000,15001,size=N,dtype=np.int16)}
maxaudio=0.
for name,pcm in fixtures.items():
 y=run('audio',pcm.tolist())['log_power'];x=pcm.astype(np.float64)/32768;x-=x.mean();w=.5-.5*np.cos(2*np.pi*n/N)
 ref=np.log(np.maximum(abs(np.fft.rfft(x*w))**2/N**2,1e-12))
 err=float(np.max(abs(np.array(y)-ref)));maxaudio=max(maxaudio,err);assert err<3e-6,(name,err)
 if name in ['silence','dc']:assert max(abs(v-math.log(1e-12)) for v in y)<3e-6
 if name=='bin16':assert np.argmax(y)==16
 known['audio_'+name]={'peak_bin':int(np.argmax(y)),'selected_bins':{str(k):y[k] for k in [0,15,16,17,128]}}
for bad in [[0]*255,[0]*257,['bad']+[0]*255,[32768]+[0]*255,[-32769]+[0]*255,[.5]+[0]*255,['nan']+[0]*255,['inf']+[0]*255]:run('audio',bad,False)
report={'status':'PASS','motion_windows':count,'rotation_checks':1,'motion_invalid_cases':5,'maximum_motion_feature_error':maxf,'maximum_motion_distance_error':maxd,'audio_fixtures':6,'audio_invalid_cases':8,'maximum_audio_log_power_error':maxaudio,'oracle':'NumPy 2.2.6 float64 rfft; C direct DFT; tolerance 3e-6','hardware':'not run'}
print(json.dumps(report,indent=2));(D/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(D/'known_answers.json').write_text(json.dumps(known,indent=2)+'\n')
