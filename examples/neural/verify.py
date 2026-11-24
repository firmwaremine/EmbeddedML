#!/usr/bin/env python3
import json,subprocess,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import train
from train_neural import qinfer
model=json.loads((ROOT/'neural/generated/neural_model.json').read_text())
exe=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'build-c/eml_c_cli'
rows=train.load_csv(ROOT/'data/windows.csv')
maxerr=0.;count=0
for r in rows:
    z=(np.array(train.features(r['raw']))-model['mean'])/model['scale']
    # Reference the exact float32 values transmitted to the C input boundary.
    z=np.array(z,dtype=np.float32).astype(np.float64)
    p=subprocess.run([str(exe)]+(sys.argv[2:] or ['neural']),input=' '.join(map(str,z)),text=True,capture_output=True,check=True)
    got=json.loads(p.stdout);expected,logits,_,sat=qinfer(z,model['quant'])
    assert expected==got['integer_label'] and logits==got['integer_logits'] and sat==got['clipped_hidden']
    fl=np.maximum(z@np.array(model['w1'])+model['b1'],0)@np.array(model['w2'])+model['b2']
    assert int(fl.argmax())==got['float_label']
    for a,b in zip(got['float_logits'],fl):maxerr=max(maxerr,abs(a-b));assert math.isclose(a,b,rel_tol=1e-5,abs_tol=2e-5)
    count+=1
# Quantizer boundary and far-range checks. No probability claims.
q=model['quant'];sx=2.**q['ex']
for z in [[0,0,0],[sx*.5,0,0],[-sx*.5,0,0],[1e6,-1e6,1e6]]:
    p=subprocess.run([str(exe)]+(sys.argv[2:] or ['neural']),input=' '.join(map(str,z)),text=True,capture_output=True,check=True);got=json.loads(p.stdout)
    pred,logits,_,_=qinfer(np.array(z,dtype=np.float32),q)
    assert got['integer_label']==pred and got['integer_logits']==logits
for bad in ['', '0 0', '0 0 0 0','nan 0 0','inf 0 0','2x 0 0']:
    assert subprocess.run([str(exe)]+(sys.argv[2:] or ['neural']),input=bad,text=True,capture_output=True).returncode==2
print(json.dumps(dict(status='PASS',windows=count,integer_accumulators='exact match',maximum_absolute_float_logit_error=maxerr,
    quantization_boundary_cases=4,invalid_input_cases=6),indent=2))
