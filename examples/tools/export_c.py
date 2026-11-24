from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];C=R/'c_core';C.mkdir(exist_ok=True)
m=json.loads((R/'generated/model.json').read_text());n=json.loads((R/'neural/generated/neural_model.json').read_text())
def arr(a,integer=False):
 if isinstance(a[0],list):return '{'+','.join(arr(x,integer) for x in a)+'}'
 return '{'+','.join(str(int(x)) if integer else f'{x:.9e}f' for x in a)+'}'
s='#ifndef EML_MODEL_DATA_H\n#define EML_MODEL_DATA_H\n#include <stdint.h>\n'
for k in ['mean','scale','centers']:
 dim='[3][3]' if k=='centers' else '[3]';s+=f'static const float eml_{k}{dim} = {arr(m[k])};\n'
s+='static const char *const eml_labels[3] = {"idle","smooth","rough"};\n'
for k in ['mean','scale','w1','b1','w2','b2']:
 value=n[k];dims=f'[{len(value)}]'+(f'[{len(value[0])}]' if isinstance(value[0],list) else '')
 s+=f'static const float emln_{k}{dims} = {arr(value)};\n'
q=n['quant']
for k in ['w1','b1','w2','b2']:
 value=q[k];dims=f'[{len(value)}]'+(f'[{len(value[0])}]' if isinstance(value[0],list) else '')
 s+=f'static const {"int32_t" if "b" in k else "int8_t"} emln_q{k}{dims} = {arr(value,True)};\n'
for k in ['ex','ew1','eh','ew2']:s+=f'#define EMLN_{k.upper()} ({q[k]})\n'
s+='#endif\n';(C/'model_data.h').write_text(s)
g=json.loads((R/'generated/golden.json').read_text());(C/'replay_data.h').write_text('#ifndef EML_REPLAY_DATA_H\n#define EML_REPLAY_DATA_H\nstatic const float eml_replay_samples[3][64] = '+arr([x['raw'] for x in g])+';\n#endif\n')
print('C model and replay headers exported')
