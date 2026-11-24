"""Original deterministic geometry reference. No object detector or image model."""
import math,json
from pathlib import Path
D=Path(__file__).resolve().parent
def valid(b):return len(b)==4 and all(math.isfinite(v) for v in b) and b[2]>b[0] and b[3]>b[1]
def iou(a,b):
 if not valid(a) or not valid(b):raise ValueError('invalid half-open box')
 inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
 return inter/((a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter)
def nms(items,threshold):
 if not 0<=threshold<=1:raise ValueError('threshold')
 if any(not valid(x['box']) or not math.isfinite(x['score']) or not 0<=x['score']<=1 for x in items):raise ValueError('item')
 # Equal scores keep source order. Suppression is per class, strictly > threshold.
 pending=sorted(enumerate(items),key=lambda p:(-p[1]['score'],p[0]));kept=[]
 for index,item in pending:
  if not any(k['class']==item['class'] and iou(k['box'],item['box'])>threshold for k in kept):kept.append(dict(item,index=index))
 return kept
if __name__=='__main__':
 a=[0,0,10,10];b=[5,0,15,10]
 assert iou(a,a)==1 and abs(iou(a,b)-1/3)<1e-15 and iou(a,[10,0,20,10])==0
 items=[{'box':a,'score':.9,'class':0},{'box':[1,1,11,11],'score':.9,'class':0},{'box':[1,1,11,11],'score':.8,'class':1},{'box':[20,20,30,30],'score':.7,'class':0}]
 out=nms(items,.5);assert [x['index'] for x in out]==[0,2,3]
 assert len(nms([items[0],items[0]],1))==2 # Strictly greater, equality retained.
 for bad in [[0,0,0,1],[1,0,0,1],[0,0,float('nan'),1]]:
  try:iou(a,bad);raise AssertionError('accepted invalid')
  except ValueError:pass
 report={'iou_overlap':iou(a,b),'nms_kept_original_indices':[x['index'] for x in out],'nms_threshold':.5,'box_convention':'half-open x0,y0,x1,y1','scope':'geometry unit fixtures only, not detection accuracy'}
 (D/'box_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
