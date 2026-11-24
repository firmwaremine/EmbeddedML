"""Exact illustrative arithmetic, not measured latency/current or WCET analysis."""
from decimal import Decimal as D
import json
from pathlib import Path
R=Path(__file__).resolve().parent
# Half-open byte-buffer lifetimes [start,end). Reuse at equal boundary allowed.
buffers=[('capture',768,0,2),('features',12,1,4),('scratch',512,1,2),('log',256,3,5)]
peak=max(sum(size for name,size,a,b in buffers if a<=t<b) for t in range(5))
assert peak==1292
stages=[('capture_delivery',2000),('features',1800),('inference',900),('policy',100),('logging',1200)]
latency=sum(v for k,v in stages);period=10000
assert latency==6000 and period-latency==4000
# Three sequential nonoverlapping hypothetical states, mA * ms /1000 = mC.
states=[('active',D('80'),D('20')),('radio',D('120'),D('10')),('sleep',D('0.2'),D('970'))]
charge=sum(current*ms/1000 for name,current,ms in states)
period_ms=sum(ms for name,current,ms in states);avg=charge/(period_ms/1000);energy_mj=charge*D('3.3')
assert charge==D('2.994') and energy_mj==D('9.8802')
# Hypothetical single-server FIFO replay: interarrival10ms, jobs6/6/15/6ms.
finish=0;response=[]
for arrival,duration in [(0,6),(10,6),(20,15),(30,6)]:
 finish=max(finish,arrival)+duration;response.append(finish-arrival)
assert response==[6,6,15,11]
out={'illustrative_peak_live_payload_bytes':peak,'illustrative_serial_latency_us':latency,'illustrative_period_slack_us':period-latency,'illustrative_charge_mC':str(charge),'illustrative_energy_mJ_at_3_3V':str(energy_mj),'illustrative_average_current_mA':str(avg),'fifo_response_ms':response,'deadline_misses_at_10ms':sum(v>10 for v in response),'scope':'invented values; no measured device timing/power or schedulability proof'}
(R/'budget_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
