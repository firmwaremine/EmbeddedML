"""Train a diagonal normal-reference score, validation quantile, untouched test."""
from pathlib import Path
import math,random,json
D=Path(__file__).resolve().parent
def data(session,count=40):
 r=random.Random(44119+session)
 for _ in range(count):yield [r.gauss(1,.08),r.gauss(.2,.02),r.gauss(.1,.015)]
train=[x for s in range(12) for x in data(s)]
mean=[sum(x[i] for x in train)/len(train) for i in range(3)]
scale=[math.sqrt(sum((x[i]-mean[i])**2 for x in train)/len(train)) for i in range(3)]
def score(x):return sum(((x[i]-mean[i])/scale[i])**2 for i in range(3))
validation=sorted(score(x) for s in range(12,16) for x in data(s))
# Empirical nearest-rank 99th percentile, fixed in advance; strict > is anomalous.
rank=math.ceil(.99*len(validation));threshold=validation[rank-1]
test=[score(x) for s in range(16,20) for x in data(s)]
shifted=[score([x[0]+.3,x[1],x[2]]) for s in range(16,20) for x in data(s)]
out={'mean':mean,'scale':scale,'threshold':threshold,'rule':'score > threshold','validation_rank_1_based':rank,'train_n':len(train),'validation_n':len(validation),'test_n':len(test),'test_normal_flagged':sum(v>threshold for v in test),'test_shifted_flagged':sum(v>threshold for v in shifted),'seed':'44119+session','scope':'synthetic independent feature vectors, no diagnosis or field rate'}
(D/'anomaly_model.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
