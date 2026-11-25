from pathlib import Path
import numpy as np,json,ctypes,subprocess,wave,time,hashlib
R=Path(__file__).resolve().parent
z=np.load(R/'model.npz');header=['/* Original trained teaching model. See DATASET.md and report.json. */']
for key,v in z.items():
 vals=[f'{float(x):.9e}f' for x in v.ravel()];header.append(f'static const float kws_{key}[{len(vals)}]={{\n'+',\n'.join(','.join(vals[i:i+12]) for i in range(0,len(vals),12))+'\n};')
(R/'model_data.h').write_text('\n'.join(header)+'\n')
subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',str(R/'kws.c'),'-lm','-o',str(R/'libkws.so')],check=True)
lib=ctypes.CDLL(str(R/'libkws.so'));fp=np.ctypeslib.ndpointer(dtype=np.float32,flags='C_CONTIGUOUS');ip=np.ctypeslib.ndpointer(dtype=np.int16,flags='C_CONTIGUOUS');lib.kws_run.argtypes=[ip,fp,fp];lib.kws_run.restype=ctypes.c_int
manifest=json.loads((R/'split_manifest.json').read_text());test=[x for x in manifest['files'] if x['split']==2];feat=np.load(R/'features.npz');ids=np.where(feat['S']==2)[0];reference=feat['X'][ids];X=(reference-z['mean'])/z['std'];py=np.maximum(X@z['w1'].T+z['b1'],0)@z['w2'].T+z['b2'];feature_err=0;logit_err=0;matches=0;cm=np.zeros((5,5),int);times=[]
for i,row in enumerate(test):
 p=R.parent/'data/mini_speech_commands'/row['path']
 with wave.open(str(p)) as w:raw=np.frombuffer(w.readframes(w.getnframes()),'<i2')
 pcm=np.zeros(16000,np.int16);pcm[:len(raw)]=raw;f=np.zeros(1176,np.float32);out=np.zeros(5,np.float32);start=time.perf_counter();pred=lib.kws_run(pcm,f,out);times.append((time.perf_counter()-start)*1000);feature_err=max(feature_err,float(np.max(np.abs(f-reference[i]))));logit_err=max(logit_err,float(np.max(np.abs(out-py[i]))));matches+=pred==py[i].argmax();cm[feat['Y'][ids[i]],pred]+=1
 if i==0:
  pcm.tofile(R/'replay.pcm');(R/'selftest_data.h').write_text('static const int16_t kws_selftest_pcm[16000]={'+','.join(str(int(x)) for x in pcm)+'};\nstatic const float kws_selftest_logits[5]={'+','.join(f'{float(x):.9e}f' for x in py[i])+'};\n')
report=dict(test_clips=len(test),label_agreement=int(matches),max_logmel_abs_error=feature_err,max_logit_abs_error=logit_err,c_confusion_matrix=cm.tolist(),c_test_accuracy=float(cm.trace()/cm.sum()),host_ms=dict(median=float(np.median(times)),p95=float(np.percentile(times,95)),maximum=float(max(times))),scope='Host x86-64 measurements, not Korvo timing; float tolerance, not integer exactness',model_header_sha256=hashlib.sha256((R/'model_data.h').read_bytes()).hexdigest())
assert matches==len(test),report
assert feature_err<.02 and logit_err<.02,report
(R/'c_parity_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
