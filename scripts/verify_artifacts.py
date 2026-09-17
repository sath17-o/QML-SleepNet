from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'pretrained/ARTIFACT_MANIFEST.json'

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main() -> None:
    m=json.loads(MAN.read_text(encoding='utf-8'))
    failures=[]
    for a in m['artifacts']:
        p=ROOT/a['file']
        if not p.is_file():
            failures.append(f"missing: {a['file']}")
            continue
        got=sha256(p)
        if p.stat().st_size != a['bytes']:
            failures.append(f"size mismatch: {a['file']}")
        if got != a['sha256']:
            failures.append(f"sha256 mismatch: {a['file']} expected={a['sha256']} got={got}")
        print(f"PASS {a['file']} {got}")

    q=ROOT/'precomputed/stage06_inputs/quantum_features_for_final_stage06.npz'
    c=ROOT/'precomputed/stage06_inputs/causal16_for_final_stage06.npz'
    for p, required in [
        (q, {'learn_uids.npy','test_uids.npy','y_learn.npy','vqc_angle8_learn.npy','vqc_angle8_test.npy'}),
        (c, {'learn_uids.npy','test_uids.npy','y_learn.npy','feature_names.npy','causal16_learn.npy','causal16_test.npy'}),
    ]:
        with zipfile.ZipFile(p) as z:
            names=set(z.namelist())
        miss=required-names
        if miss: failures.append(f"{p.name}: missing NPZ members {sorted(miss)}")
        if 'y_test.npy' in names: failures.append(f"{p.name}: forbidden y_test.npy present")
    if failures:
        print('\nARTIFACT VERIFICATION FAILED',file=sys.stderr)
        for x in failures: print(' -',x,file=sys.stderr)
        raise SystemExit(1)
    print(f"\nARTIFACT VERIFICATION PASS ({len(m['artifacts'])} versioned files)")

if __name__=='__main__': main()
