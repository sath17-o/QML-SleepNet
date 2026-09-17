from __future__ import annotations
from pathlib import Path
import csv, json, math, hashlib

ROOT=Path(__file__).resolve().parents[1]
S11=ROOT/'results/manifests/STAGE11_FINAL_MANIFEST.json'
S10=ROOT/'results/manifests/STAGE10_PROMOTED_FINAL_MANIFEST.json'
XAI=ROOT/'results/manifests/XAI_PROMOTED_FINAL_MANIFEST.json'
TABLE=ROOT/'results/final/STAGE11_FINAL_RESULTS_TABLE.csv'
CONTRACT=ROOT/'config/pipeline_contract.json'
for p in [S11,S10,XAI,TABLE,CONTRACT]:
    if not p.is_file(): raise FileNotFoundError(p)

m=json.loads(S11.read_text(encoding='utf-8'))
s10=json.loads(S10.read_text(encoding='utf-8'))
xai=json.loads(XAI.read_text(encoding='utf-8'))
c=json.loads(CONTRACT.read_text(encoding='utf-8'))

final=m['final_designated_system']
expected_sha='063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f'
assert m['status']=='STAGE11_COMPLETE'
assert final['name']=='FIXED_LOGIT_PHYS_25_QML_75'
assert final['official_x_records']==35 and final['official_x_rows']==17248
assert final['prediction_sha256']==expected_sha==c['system_identities']['promoted_final']['prediction_sha256']
assert math.isclose(final['metrics']['accuracy'],0.9086270871985158,rel_tol=0,abs_tol=1e-15)
assert math.isclose(m['comparison_roles']['canonical_guide_qml']['accuracy'],0.9011479591836735,rel_tol=0,abs_tol=1e-15)
assert math.isclose(m['comparison_roles']['best_classical_only_benchmark']['accuracy'],0.9101924860853432,rel_tol=0,abs_tol=1e-12)
assert s10.get('training_performed') is False
assert xai.get('training_performed') is False

rows=list(csv.DictReader(TABLE.open(newline='',encoding='utf-8')))
names={r.get('system') for r in rows}
required={'FINAL_QML_INCLUSIVE_PROMOTED','STAGE15A_PHYSIOLOGY_CLASSICAL','CANONICAL_GUIDE_QML'}
if required-names: raise RuntimeError('Missing final comparison rows: '+repr(sorted(required-names)))

print('Frozen scientific-contract verification PASSED')
print(f"Promoted QML-inclusive accuracy: {final['metrics']['accuracy']*100:.4f}%")
print(f"Canonical guide QML accuracy: {m['comparison_roles']['canonical_guide_qml']['accuracy']*100:.4f}%")
print(f"Best classical-only benchmark: {m['comparison_roles']['best_classical_only_benchmark']['accuracy']*100:.4f}%")
print('Prediction SHA-256:',expected_sha)
print('Official-x:',final['official_x_records'],'records /',final['official_x_rows'],'rows')
print('Training performed by verifier: NO')
print('Quantum-advantage claim: NO')
