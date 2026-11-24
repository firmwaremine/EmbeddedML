#!/usr/bin/env python3
import json, math, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import train
exe=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'build-c'/'eml_c_cli'
rows=train.load_csv(ROOT/'data'/'windows.csv')
model=json.loads((ROOT/'generated'/'model.json').read_text())
max_feature=0.;max_distance=0.
for r in rows:
    p=subprocess.run([str(exe)],input=' '.join(map(str,r['raw'])),text=True,capture_output=True,check=True)
    got=json.loads(p.stdout);expected,f,ds=train.predict(model,r['raw'])
    assert got['label']==expected
    for a,b in zip(got['features'],f):
        max_feature=max(max_feature,abs(a-b));assert math.isclose(a,b,rel_tol=2e-5,abs_tol=2e-6)
    for a,b in zip(got['distances'],ds):
        max_distance=max(max_distance,abs(a-b));assert math.isclose(a,b,rel_tol=5e-5,abs_tol=2e-5)
for bad in ['', '0 '*63, '0 '*65, 'nan '+'0 '*63,'inf '+'0 '*63,'1e99 '+'0 '*63,'3x '+'0 '*63]:
    p=subprocess.run([str(exe)],input=bad,text=True,capture_output=True)
    assert p.returncode==2
print(json.dumps(dict(windows_checked=len(rows),invalid_cli_cases=7,max_absolute_feature_error=max_feature,
                     max_absolute_distance_error=max_distance,status='PASS'),indent=2))
