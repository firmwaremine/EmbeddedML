#!/usr/bin/env python3
"""Original teaching classifier. Python standard library only; synthetic signals."""
import argparse, csv, hashlib, json, math, random, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
N = 64
LABELS = ['idle', 'smooth', 'rough']

def features(x):
    if len(x) != N or not all(math.isfinite(v) for v in x):
        raise ValueError('exactly 64 finite samples required')
    mean = sum(x)/N
    return [mean, math.sqrt(sum((v-mean)**2 for v in x)/N),
            sum(abs(x[i]-x[i-1]) for i in range(1,N))/(N-1)]

def generate():
    rows=[]
    for session in range(30):
        rng=random.Random(9127+session)
        offset=rng.uniform(-0.15,0.15)
        gain=rng.uniform(0.85,1.15)
        for label in range(3):
            for window in range(8):
                phase=rng.uniform(0,2*math.pi)
                amp=[0.035,0.45,0.75][label]*gain
                cycles=[1.0,2.0,9.0][label]+rng.uniform(-0.2,0.2)
                raw=[offset+amp*math.sin(2*math.pi*cycles*i/N+phase)+rng.gauss(0,0.02) for i in range(N)]
                split='train' if session<18 else ('validation' if session<24 else 'test')
                rows.append(dict(session=session,window=window,label=label,split=split,raw=raw))
    return rows

def load_csv(path):
    rows=[]
    with open(path,newline='') as f:
        for r in csv.DictReader(f):
            label=int(r['label']); split=r['split']
            if label not in range(3) or split not in ('train','validation','test'):
                raise ValueError('invalid label or split')
            raw=[float(r[f'x{i}']) for i in range(N)]
            features(raw)
            rows.append(dict(session=r['session'],window=r['window'],label=label,split=split,raw=raw))
    sessions={}
    for r in rows:
        if r['session'] in sessions and sessions[r['session']]!=r['split']:
            raise ValueError('session crosses split boundary')
        sessions[r['session']]=r['split']
    return rows

def train(rows):
    train_rows=[r for r in rows if r['split']=='train']
    if not train_rows: raise ValueError('no training data')
    fs=[features(r['raw']) for r in train_rows]
    mu=[statistics.mean(f[j] for f in fs) for j in range(3)]
    scale=[max(statistics.pstdev(f[j] for f in fs),1e-6) for j in range(3)]
    centers=[]
    for k in range(3):
        group=[features(r['raw']) for r in train_rows if r['label']==k]
        if not group: raise ValueError('missing training class')
        centers.append([(statistics.mean(f[j] for f in group)-mu[j])/scale[j] for j in range(3)])
    return dict(mean=mu,scale=scale,centers=centers,labels=LABELS)

def predict(model,x):
    f=features(x); z=[(f[j]-model['mean'][j])/model['scale'][j] for j in range(3)]
    ds=[sum((z[j]-c[j])**2 for j in range(3)) for c in model['centers']]
    return min(range(3),key=lambda k:ds[k]),f,ds

def array(x):
    if isinstance(x[0],list): return '{'+','.join(array(v) for v in x)+'}'
    return '{'+','.join(f'{v:.9e}f' for v in x)+'}'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--csv',type=Path);args=ap.parse_args()
    rows=load_csv(args.csv) if args.csv else generate()
    model=train(rows)
    out=ROOT/'generated';out.mkdir(exist_ok=True)
    (out/'model.json').write_text(json.dumps(model,indent=2)+'\n')
    reports={}
    for split in ['train','validation','test']:
        subset=[r for r in rows if r['split']==split]
        if not subset: raise ValueError('every split must contain data')
        cm=[[0]*3 for _ in range(3)]
        for r in subset: cm[r['label']][predict(model,r['raw'])[0]]+=1
        reports[split]=dict(n=len(subset),confusion=cm,accuracy=sum(cm[i][i] for i in range(3))/len(subset))
    golden=[]
    for k in range(3):
        r=next(r for r in rows if r['label']==k and r['split']=='test')
        pred,f,ds=predict(model,r['raw']);golden.append(dict(raw=r['raw'],features=f,distances=ds,predicted=pred))
    (out/'golden.json').write_text(json.dumps(golden,indent=2)+'\n')
    with open(ROOT/'data'/'windows.csv','w',newline='') as f:
        w=csv.writer(f);w.writerow(['session','window','label','split']+[f'x{i}' for i in range(N)])
        for r in rows:w.writerow([r['session'],r['window'],r['label'],r['split']]+r['raw'])
    provenance=dict(generator_seed_rule='9127 + session',window_samples=N,sample_rate_hz_assumed=128,
        synthetic=not bool(args.csv),training_sessions=sorted(set(str(r['session']) for r in rows if r['split']=='train')),
        model_sha256=hashlib.sha256((out/'model.json').read_bytes()).hexdigest(),reports=reports)
    (out/'training_report.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps(provenance,indent=2))
if __name__=='__main__': main()
