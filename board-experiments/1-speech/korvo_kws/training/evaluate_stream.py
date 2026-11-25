from pathlib import Path
import ctypes,json,wave,numpy as np
R=Path(__file__).resolve().parent
lib=ctypes.CDLL(str(R/'libkws.so'));fp=np.ctypeslib.ndpointer(dtype=np.float32,flags='C_CONTIGUOUS');ip=np.ctypeslib.ndpointer(dtype=np.int16,flags='C_CONTIGUOUS');lib.kws_run.argtypes=[ip,fp,fp];lib.kws_run.restype=ctypes.c_int
rows=json.loads((R/'split_manifest.json').read_text())['files'];labels=['go','no','stop','yes','other']
def build(split):
 chosen=[]
 for word in ['go','no','stop','yes','down','left','right','up']:
  chosen.extend([x for x in rows if x['split']==split and x['path'].split('/')[0]==word][:20])
 stream=[];truth=[];time=0
 for x in chosen:
  stream.extend(np.zeros(32000,np.int16));time+=32000
  with wave.open(str(R.parent/'data/mini_speech_commands'/x['path'])) as w:raw=np.frombuffer(w.readframes(w.getnframes()),'<i2')
  pcm=np.zeros(16000,np.int16);pcm[:len(raw)]=raw;truth.append(dict(label=x['path'].split('/')[0],start=time/16000,end=(time+16000)/16000));stream.extend(pcm);time+=16000
 stream=np.asarray(stream,np.int16);scores=[]
 for end in range(16000,len(stream)+1,1600):
  p=stream[end-16000:end].copy();f=np.empty(1176,np.float32);o=np.empty(5,np.float32);label=lib.kws_run(p,f,o);v=np.exp(o-o.max());scores.append(dict(time=end/16000,label=int(label),confidence=float(v[label]/v.sum()),rms=float(np.sqrt(np.mean((p.astype('float32')/32768)**2)))))
 return truth,scores

def evaluate(truth,scores,threshold):
 events=[];latched=False;last=-2;release=0
 for x in scores:
  candidate=x['label']<4 and x['confidence']>=threshold and x['rms']>=.005
  if not candidate:
   release+=1
   if release>=3:latched=False
  else:
   release=0
   if not latched and x['time']-last>=1:
    events.append(dict(time=x['time'],label=labels[x['label']]));latched=True;last=x['time']
 matched=set();false=0
 for e in events:
  ids=[i for i,x in enumerate(truth) if i not in matched and x['label']==e['label'] and x['start']<=e['time']<=x['end']+1]
  if ids:matched.add(ids[0])
  else:false+=1
 targets=sum(x['label'] in labels[:4] for x in truth);tp=len(matched);f1=2*tp/max(1,2*tp+false+targets-tp)
 return dict(threshold=threshold,target_trials=targets,correct=tp,missed=targets-tp,unmatched_events=false,event_f1=f1,events=events)
validation,vs=build(1);candidates=[evaluate(validation,vs,x) for x in [.5,.6,.7,.8,.9]];best=max(candidates,key=lambda x:(x['event_f1'],x['threshold']));test,ts=build(2);result=evaluate(test,ts,best['threshold']);report=dict(validation_candidates=[{k:v for k,v in x.items() if k!='events'} for x in candidates],selected_threshold=best['threshold'],test=result,scope='Constructed host stream using 20 real held-out clips per original word and digital silence. 80 target + 80 other-word trials. Not continuous naturally spoken audio, ambient noise or a device result. Threshold selected on separate validation speakers only. Single-hit gate, 100ms hop, 3 noncandidates release latch, 1s cooldown, RMS >=0.005.')
(R/'stream_report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='test'},indent=2));print({k:v for k,v in result.items() if k!='events'})
