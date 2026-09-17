import csv, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def test_promoted_final_contract():
    m=json.loads((ROOT/'results/manifests/STAGE11_FINAL_MANIFEST.json').read_text())
    f=m['final_designated_system']
    assert m['status']=='STAGE11_COMPLETE'
    assert f['name']=='FIXED_LOGIT_PHYS_25_QML_75'
    assert f['official_x_records']==35 and f['official_x_rows']==17248
    assert f['prediction_sha256']=='063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f'

def test_guide_source_lock():
    m=json.loads((ROOT/'config/guide_source_manifest.json').read_text())
    assert len(m['images'])==5
    for x in m['images']:
        p=ROOT/x['file']; assert p.is_file(); assert sha(p)==x['sha256']
    assert m['raw_from_scratch_claim'] is False

def test_execution_manifest_notebooks_exist():
    e=json.loads((ROOT/'config/execution_manifest.json').read_text())
    for section in ['guide_replay_chain','promoted_evidence_chain']:
        for s in e[section]: assert (ROOT/s['notebook']).is_file()
    assert e['identity_boundary']['guide_native_endpoint']=='pretrained/stage06/qml_sleepnet_final_guide_corrected.pt'

def test_guide_invariants_and_nonclaims():
    s3=json.loads((ROOT/'results/manifests/guide/STAGE03_GUIDE_REBUILD_MANIFEST.json').read_text())
    q=json.loads((ROOT/'results/manifests/guide/STAGE04_AUDITED_V3_MANIFEST.json').read_text())
    s6=json.loads((ROOT/'results/manifests/guide/FINAL_GUIDE_CORRECTED_MANIFEST.json').read_text())
    assert s3['ahi_input_feature_used'] is False
    assert s3['task_b_osa_csa_mixed_ground_truth_created'] is False
    assert q['source_locked']['classical_encoder']=='128->64->32->8'
    assert q['source_locked']['qubits']==8 and q['source_locked']['vqc_depth']==4
    assert s6['task']=='Task A binary Apnea vs Normal'
    assert s6['official_x_labels_used'] is False

def test_frozen_artifact_hashes():
    m=json.loads((ROOT/'pretrained/ARTIFACT_MANIFEST.json').read_text())
    for a in m['artifacts']:
        p=ROOT/a['file']; assert p.is_file(); assert p.stat().st_size==a['bytes']; assert sha(p)==a['sha256']

def test_final_table_has_three_roles():
    rows=list(csv.DictReader((ROOT/'results/final/STAGE11_FINAL_RESULTS_TABLE.csv').open()))
    names={r['system'] for r in rows}
    assert {'FINAL_QML_INCLUSIVE_PROMOTED','STAGE15A_PHYSIOLOGY_CLASSICAL','CANONICAL_GUIDE_QML'} <= names

def test_real_x01_reproduction_receipt():
    r=json.loads((ROOT/'results/validation/FROZEN_STAGE06_X01_REPRODUCTION.json').read_text())
    assert r['status']=='PASS'
    assert r['official_x_labels_read'] is False
    assert r['rows']==522
    assert r['max_abs_probability_difference_vs_frozen_reference'] <= r['tolerance_used']
    assert r['checkpoint_sha256']=='a04ac77bd285bb04077a7ffd294cb5b0ad805a9ec2560b0f050c03acce2e262b'
