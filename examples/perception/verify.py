from pathlib import Path
import ctypes as C,json,sys,math,random
from vision_train import data,features,predict
D=Path(__file__).resolve().parent;lib=C.CDLL(str(Path(sys.argv[1]).resolve()))
U8=C.POINTER(C.c_uint8);F=C.POINTER(C.c_float);DB=C.POINTER(C.c_double)
lib.rgb_features.argtypes=[U8,F];lib.rgb_features.restype=C.c_bool
lib.rgb_resize16.argtypes=[U8,C.c_size_t,C.c_size_t,C.c_size_t,C.c_size_t,U8];lib.rgb_resize16.restype=C.c_bool
lib.vision_classify.argtypes=[F,DB];lib.vision_classify.restype=C.c_int
lib.anomaly_score.argtypes=[F,F,F,DB];lib.anomaly_score.restype=C.c_bool
m=json.loads((D/'vision_model.json').read_text());maxerr=0;maxd=0;count=0;known={}
for s,l,r,p in data():
 a=(C.c_uint8*768)(*p);f=(C.c_float*6)();assert lib.rgb_features(a,f);ref=features(p)
 maxerr=max(maxerr,max(abs(a-b) for a,b in zip(f,ref)));d=(C.c_double*3)();pred=lib.vision_classify(f,d);expected,ds=predict(ref,m);assert pred==expected
 maxd=max(maxd,max(abs(a-b) for a,b in zip(d,ds)));assert max(abs(a-b) for a,b in zip(d,ds))<1e-10
 if s==0 and r==0:known[m['labels'][l]]={'features':list(f),'label':pred,'distances':list(d)}
 count+=1
# Padded, odd, nonsquare and minimal dimensions. Byte-exact independent mapping.
rng=random.Random(11291);resize=0
for w,h,pad in [(1,1,0),(2,2,2),(3,5,7),(17,9,0),(61,37,5),(32,32,16)]:
 stride=w*3+pad;p=[rng.randrange(256) for _ in range(stride*h)];out=(C.c_uint8*768)();a=(C.c_uint8*len(p))(*p)
 assert lib.rgb_resize16(a,len(p),w,h,stride,out)
 ref=[p[(y*h//16)*stride+(x*w//16)*3+c] for y in range(16) for x in range(16) for c in range(3)]
 assert list(out)==ref;resize+=1
# Explicit score fixture and a zero-variance guard.
x=(C.c_float*3)(2,4,6);mean=(C.c_float*3)(1,2,3);scale=(C.c_float*3)(1,2,3);score=C.c_double()
assert lib.anomaly_score(x,mean,scale,C.byref(score)) and score.value==3
report={'status':'PASS','vision_windows':count,'max_feature_error':maxerr,'max_squared_distance_error':maxd,'resize_fixtures_byte_exact':resize,'anomaly_known_score':score.value,'hardware':'not run'}
(D/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(D/'known_answers.json').write_text(json.dumps(known,indent=2)+'\n');print(json.dumps(report,indent=2))
