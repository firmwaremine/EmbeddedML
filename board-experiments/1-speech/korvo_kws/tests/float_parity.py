"""Compare the single-precision firmware features/network with the earlier
double-precision reference (tests/kws_double_reference.c) on every held-out test clip.
Needs gcc and the speech clips in the repository's realdata/data/mini_speech_commands.
Run from the korvo_kws folder: python tests/float_parity.py"""
import json,subprocess,tempfile,wave
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
root=R.parents[2]/'realdata/data/mini_speech_commands'
tmp=Path(tempfile.mkdtemp())
flags=['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(R/'main')]
subprocess.run(flags+['-c',str(R/'main/kws.c'),'-o',str(tmp/'new.o')],check=True)
subprocess.run(['gcc','-std=c11','-O2','-I',str(R/'main'),'-Dkws_features=kws_features_ref','-Dkws_predict=kws_predict_ref','-Dkws_run=kws_run_ref','-Dkws_confidence=kws_confidence_ref','-Wno-unused','-c',str(R/'tests/kws_double_reference.c'),'-o',str(tmp/'ref.o')],check=True)
subprocess.run(flags+[str(R/'tests/float_parity.c'),str(tmp/'new.o'),str(tmp/'ref.o'),'-lm','-o',str(tmp/'fp')],check=True)
manifest=json.loads((R/'training/split_manifest.json').read_text())
paths=[]
for i,x in enumerate(f for f in manifest['files'] if f['split']==2):
    with wave.open(str(root/x['path'])) as w:raw=np.frombuffer(w.readframes(w.getnframes()),'<i2')
    p=np.zeros(16000,np.int16);p[:min(len(raw),16000)]=raw[:16000];f=tmp/f'{i}.pcm';p.tofile(f);paths.append(str(f))
r=subprocess.run([str(tmp/'fp')],input='\n'.join(paths)+'\n',text=True,capture_output=True)
print(r.stdout.strip());raise SystemExit(r.returncode)
