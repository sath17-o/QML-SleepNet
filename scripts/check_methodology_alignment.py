from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    failures=[]
    src=json.loads((ROOT/'config/guide_source_manifest.json').read_text())
    for im in src['images']:
        p=ROOT/im['file']
        if not p.is_file(): failures.append(f"missing methodology source {im['file']}"); continue
        if sha(p)!=im['sha256']: failures.append(f"methodology source hash mismatch {im['file']}")

    s3=json.loads((ROOT/'results/manifests/guide/STAGE03_GUIDE_REBUILD_MANIFEST.json').read_text())
    b=json.loads((ROOT/'results/manifests/guide/STAGE04_FULLGRID_MANIFEST.json').read_text())
    q=json.loads((ROOT/'results/manifests/guide/STAGE04_AUDITED_V3_MANIFEST.json').read_text())
    c=json.loads((ROOT/'results/manifests/guide/STAGE05_CAUSAL_CORE_MANIFEST.json').read_text())
    s6=json.loads((ROOT/'results/manifests/guide/FINAL_GUIDE_CORRECTED_MANIFEST.json').read_text())
    th=json.loads((ROOT/'results/manifests/guide/FINAL_OPERATING_THRESHOLD.json').read_text())

    checks=[
      (s3.get('dataset')=='Apnea-ECG','Stage03 dataset must be Apnea-ECG'),
      (s3.get('fs_hz')==100 and s3.get('epoch_seconds')==60,'Stage03 geometry must be 100 Hz / 60 s'),
      (len(s3.get('learn_records',[]))==35 and len(s3.get('official_test_records',[]))==35,'Expected 35 learn + 35 official-x records'),
      (s3.get('official_test_labels_accessed_for_model_selection') is False,'Official-x labels must remain sealed in model selection'),
      (s3.get('ahi_input_feature_used') is False,'AHI must remain excluded from model input'),
      (s3.get('task_b_osa_csa_mixed_ground_truth_created') is False,'OSA/CSA/Mixed ground truth must not be fabricated'),
      (b.get('official_test_labels_used') is False,'Bridge must not use official-x labels'),
      (b.get('winning_selector')=='S192','Published bridge selector identity mismatch'),
      (b.get('bridge_model_sha256')=='361183f36647c0e44e1c59860fa1c79b04e90df87b8961dc67e3301a739a33a3','Bridge checkpoint SHA mismatch in source manifest'),
      (q.get('source_locked',{}).get('classical_encoder')=='128->64->32->8','QML pre-encoder geometry mismatch'),
      (q.get('source_locked',{}).get('qubits')==8,'QML qubit count mismatch'),
      (q.get('source_locked',{}).get('vqc_depth')==4 and q.get('source_locked',{}).get('vqc_quantum_parameters')==96,'VQC depth/parameter specification mismatch'),
      (q.get('source_locked',{}).get('measurement')=='Pauli-Z expectation values','QML measurement specification mismatch'),
      (q.get('official_test_labels_used_for_training_or_selection') is False,'QML stage official-x label boundary violated'),
      (c.get('graph_discovery')==['PC','FCI','NOTEARS','LiNGAM'],'Stage05 graph discovery set mismatch'),
      (c.get('causal16',{}).get('official_test_labels_used') is False,'Causal16 official-x label boundary violated'),
      (s6.get('task')=='Task A binary Apnea vs Normal','Stage06 must remain Task A binary'),
      (s6.get('official_x_labels_used') is False,'Stage06 official-x label boundary violated'),
      ('QML8 + temporal512 + gated causal16' in s6.get('fusion',''),'Stage06 fusion geometry mismatch'),
      (abs(float(th.get('frozen_threshold'))-0.415)<1e-12 and th.get('official_x_labels_used') is False,'Operating-threshold contract mismatch'),
    ]
    for ok,msg in checks:
        if not ok: failures.append(msg)
    if failures:
        print('METHODOLOGY ALIGNMENT CHECK FAILED',file=sys.stderr)
        for x in failures: print(' -',x,file=sys.stderr)
        raise SystemExit(1)
    print(f"METHODOLOGY ALIGNMENT PASS: {len(src['images'])} source images + {len(checks)} implementation invariants")

if __name__=='__main__': main()
