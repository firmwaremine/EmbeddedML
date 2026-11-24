"""One-to-one greedy event matching within a declared onset tolerance."""
import json,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
observed=[int(v) for v in subprocess.check_output([str(Path(sys.argv[1]).resolve())],text=True).split()]
assert observed==[1040,5040,9040],observed
# Two target intervals; the 9s burst is intentionally a false trigger.
truth=[(1000,1260),(5000,5200)];matched=set();latencies=[];false=[]
for t in observed:
 candidates=[i for i,(on,off) in enumerate(truth) if i not in matched and on<=t<=off+200]
 if candidates:
  i=candidates[0];matched.add(i);latencies.append(t-truth[i][0])
 else:false.append(t)
negative_ms=12000-sum(off-on for on,off in truth)
out={'events_ms':observed,'matched_targets':len(matched),'missed_targets':len(truth)-len(matched),'false_events':len(false),'onset_latency_ms':latencies,'negative_audio_ms':negative_ms,'false_per_negative_hour':len(false)/(negative_ms/3600000),'scope':'tiny fabricated score trace; arithmetic test, NOT a measured speech detector false-activation rate'}
(D/'policy_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
