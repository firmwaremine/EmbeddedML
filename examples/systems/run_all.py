"""Host acceptance runner. Does not flash, contact a sensor or approve deployment."""
from pathlib import Path
import subprocess,sys,tempfile,json,platform
E=Path(__file__).resolve().parents[1];steps=[]
def run(*args):
 print('+',' '.join(map(str,args)),flush=True);subprocess.run(list(map(str,args)),cwd=E,check=True);steps.append(list(map(str,args)))
with tempfile.TemporaryDirectory(prefix='eml-host-') as tmp:
 B=Path(tmp)
 for name,src in [('core','c_core'),('app','applications'),('perception','perception'),('systems','systems')]:
  run('cmake','-S',src,'-B',B/name,'-DCMAKE_BUILD_TYPE=Debug');run('cmake','--build',B/name,'-j2')
  if name!='app':run('ctest','--test-dir',B/name,'--output-on-failure')
 run(sys.executable,'tests/verify.py',B/'core/eml_c_cli')
 run(sys.executable,'neural/verify.py',B/'core/eml_c_cli','neural')
 run(sys.executable,'applications/verify.py',B/'app/sensing_cli')
 run(sys.executable,'perception/verify.py',B/'perception/libperception.so')
 run(sys.executable,'perception/evaluate_events.py',B/'perception/policy_trace')
 for script in ['perception/boxes.py','systems/budget.py','systems/release_gate.py']:run(sys.executable,script)
report={'status':'PASS','platform':platform.platform(),'python':platform.python_version(),'commands_succeeded':len(steps),'scope':'ordinary Linux host builds and listed fixtures only; no hardware/target or production release approval'}
(E/'systems/acceptance_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
