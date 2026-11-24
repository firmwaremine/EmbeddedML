#!/usr/bin/env python3
"""Emit one CSV row for piping to eml_cli. Not a sensor-capture driver."""
import argparse,csv
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--row',type=int,default=0);a=p.parse_args()
if a.row<0: p.error('row must be nonnegative')
with open(Path(__file__).resolve().parents[1]/'data'/'windows.csv') as f:
    for i,r in enumerate(csv.DictReader(f)):
        if i==a.row:
            print(' '.join(r[f'x{j}'] for j in range(64)));break
    else: p.error('row outside dataset')
