from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FS=100
EPOCH_SECONDS=60
EPOCH_SAMPLES=FS*EPOCH_SECONDS
DROPOUT=0.4
POOL=10


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def verify_bundled_artifact(rel: str) -> Path:
    man=json.loads((ROOT/'pretrained/ARTIFACT_MANIFEST.json').read_text())
    row=next((x for x in man['artifacts'] if x['file']==rel),None)
    if row is None: raise RuntimeError(f'Artifact not registered: {rel}')
    p=ROOT/rel
    if not p.is_file(): raise FileNotFoundError(p)
    if p.stat().st_size!=row['bytes'] or sha256(p)!=row['sha256']:
        raise RuntimeError(f'Artifact integrity failure: {rel}')
    return p


def main() -> None:
    ap=argparse.ArgumentParser(description='Run the published Stage06 hybrid checkpoint. Official-x labels are never read.')
    ap.add_argument('--stage02-dir', required=True, help='Directory containing {record}_preprocessed.npz files')
    ap.add_argument('--split', choices=['official-x','learn'], default='official-x')
    ap.add_argument('--output', default='outputs/stage06_predictions.csv')
    ap.add_argument('--batch-size', type=int, default=128)
    ap.add_argument('--device', default='auto', choices=['auto','cpu','cuda'])
    ap.add_argument('--records', default='', help='Optional comma-separated record filter, e.g. x01,x02')
    ap.add_argument('--limit', type=int, default=0, help='Optional first-N row limit for an execution smoke test')
    ap.add_argument('--threshold', type=float, default=None, help='Override the published Stage06 operating threshold. Default reads FINAL_OPERATING_THRESHOLD.json.')
    ap.add_argument('--compare-reference', action='store_true', help='Compare probabilities against the bundled Stage06 reference for selected rows.')
    ap.add_argument('--tolerance', type=float, default=1e-4, help='Maximum absolute probability difference allowed by --compare-reference.')
    args=ap.parse_args()

    try:
        import numpy as np
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except Exception as e:
        raise SystemExit(f'Stage06 inference requires numpy + torch. Install requirements-inference.txt. Details: {e}')

    class TemporalEncoder(nn.Module):
        def __init__(self):
            super().__init__()
            self.c3=nn.Conv1d(1,64,3,padding=1)
            self.c5=nn.Conv1d(1,64,5,padding=2)
            self.c7=nn.Conv1d(1,64,7,padding=3)
            self.bn=nn.BatchNorm1d(192)
            self.pool=nn.MaxPool1d(POOL,POOL)
            self.bilstm=nn.LSTM(192,128,num_layers=2,batch_first=True,bidirectional=True,dropout=DROPOUT)
            self.attn=nn.MultiheadAttention(256,1,dropout=DROPOUT,batch_first=True)
        def forward(self,x):
            h=torch.cat([self.c3(x),self.c5(x),self.c7(x)],dim=1)
            h=self.pool(F.relu(self.bn(h))).transpose(1,2)
            h,_=self.bilstm(h)
            h,_=self.attn(h,h,h,need_weights=False)
            return torch.cat([h.mean(dim=1),h.max(dim=1).values],dim=1)

    class HybridModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.temporal=TemporalEncoder()
            self.causal_gate=nn.Linear(16,16)
            self.fusion256=nn.Linear(536,256)
            self.fc128=nn.Linear(256,128)
            self.fc64=nn.Linear(128,64)
            self.out=nn.Linear(64,2)
            self.drop=nn.Dropout(DROPOUT)
        def fuse(self,temporal512,qml8,causal16):
            gate=torch.sigmoid(self.causal_gate(causal16))
            causal_gated=causal16*gate
            z=torch.cat([qml8,temporal512,causal_gated],dim=1)
            z=F.relu(self.fusion256(z))
            h=self.drop(F.relu(self.fc128(z)))
            h=self.drop(F.relu(self.fc64(h)))
            return self.out(h)
        def forward(self,ecg,qml8,causal16):
            t=self.temporal(ecg)
            return self.fuse(t,qml8,causal16),t

    model_path=verify_bundled_artifact('pretrained/stage06/qml_sleepnet_final_guide_corrected.pt')
    q_path=verify_bundled_artifact('precomputed/stage06_inputs/quantum_features_for_final_stage06.npz')
    c_path=verify_bundled_artifact('precomputed/stage06_inputs/causal16_for_final_stage06.npz')
    ref_path=verify_bundled_artifact('results/guide_stage06/final_predictions.npz')

    q=np.load(q_path,allow_pickle=False)
    # The source causal UID arrays use dtype=object; artifact integrity is verified before this trusted load.
    c=np.load(c_path,allow_pickle=True)
    if 'y_test' in q.files or 'y_test' in c.files:
        raise RuntimeError('Official-x label boundary violated: y_test present in Stage06 inputs.')

    if args.split=='official-x':
        uids=np.asarray(q['test_uids']).astype(str)
        qml=np.asarray(q['vqc_angle8_test'],dtype=np.float32)
        cu=np.asarray(c['test_uids']).astype(str)
        causal=np.asarray(c['causal16_test'],dtype=np.float32)
        y=None
        ref_key='test_probability'
    else:
        uids=np.asarray(q['learn_uids']).astype(str)
        qml=np.asarray(q['vqc_angle8_learn'],dtype=np.float32)
        cu=np.asarray(c['learn_uids']).astype(str)
        causal=np.asarray(c['causal16_learn'],dtype=np.float32)
        y=np.asarray(q['y_learn'],dtype=np.int8)
        if not np.array_equal(y,np.asarray(c['y_learn'],dtype=np.int8)):
            raise RuntimeError('Learning-label alignment mismatch between Stage04 and Stage05 arrays.')
        ref_key='learn_probability'
    if not np.array_equal(uids,cu): raise RuntimeError('Stage04/Stage05 UID alignment mismatch.')
    if qml.shape!=(len(uids),8) or causal.shape!=(len(uids),16): raise RuntimeError('Stage06 input geometry mismatch.')
    if not np.isfinite(qml).all() or not np.isfinite(causal).all(): raise RuntimeError('Non-finite Stage06 input features.')

    selected=np.arange(len(uids),dtype=np.int64)
    if args.records:
        wanted={r.strip() for r in args.records.split(',') if r.strip()}
        selected=np.asarray([i for i,u in enumerate(uids) if u.rsplit(':',1)[0] in wanted],dtype=np.int64)
        missing=wanted-{uids[i].rsplit(':',1)[0] for i in selected}
        if missing: raise SystemExit(f'Requested records absent from {args.split}: {sorted(missing)}')
    if args.limit>0: selected=selected[:args.limit]
    if len(selected)==0: raise SystemExit('No rows selected.')

    if args.device=='auto': device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        if args.device=='cuda' and not torch.cuda.is_available(): raise SystemExit('CUDA requested but unavailable.')
        device=torch.device(args.device)

    try: ck=torch.load(model_path,map_location='cpu',weights_only=True)
    except TypeError: ck=torch.load(model_path,map_location='cpu')
    expected={'encoding':'angle_rx','gate':'causal16_to_gate16_on_causal_branch','clip_sd':4.0,'task':'binary Apnea vs Normal','official_x_labels_used':False}
    for k,v in expected.items():
        if ck.get(k)!=v: raise RuntimeError(f'Checkpoint metadata mismatch: {k} expected={v!r} got={ck.get(k)!r}')
    model=HybridModel().to(device)
    model.load_state_dict(ck['state_dict'],strict=True)
    model.eval()

    threshold_json=json.loads((ROOT/'results/manifests/guide/FINAL_OPERATING_THRESHOLD.json').read_text())
    threshold=float(threshold_json['frozen_threshold']) if args.threshold is None else float(args.threshold)
    if not (0.0<=threshold<=1.0): raise SystemExit('Threshold must be in [0,1].')

    s2=Path(args.stage02_dir).expanduser().resolve()
    if not s2.is_dir(): raise SystemExit(f'Stage02 directory not found: {s2}')
    probs=np.full(len(selected),np.nan,dtype=np.float64)
    sel_uids=uids[selected]
    sel_q=qml[selected]
    sel_c=causal[selected]
    position_by_record={}
    for local,(global_i,uid) in enumerate(zip(selected,sel_uids)):
        rec,ep=uid.rsplit(':',1)
        position_by_record.setdefault(rec,[]).append((local,int(ep)))

    with torch.no_grad():
        for rec,items in sorted(position_by_record.items()):
            p=s2/f'{rec}_preprocessed.npz'
            if not p.is_file(): raise FileNotFoundError(f'Missing Stage02 record: {p}')
            d=np.load(p,allow_pickle=False)
            required={'ecg_filtered','fs','n_epochs'}
            miss=required-set(d.files)
            if miss: raise RuntimeError(f'{rec}: Stage02 missing keys {sorted(miss)}')
            ecg=np.asarray(d['ecg_filtered'],dtype=np.float32)
            fs=int(np.asarray(d['fs']).item()); ne=int(np.asarray(d['n_epochs']).item())
            if fs!=FS or len(ecg)!=ne*EPOCH_SAMPLES: raise RuntimeError(f'{rec}: Stage02 geometry mismatch')
            mu=float(ecg.mean()); sd=float(ecg.std())
            if not math.isfinite(sd) or sd<1e-8: raise RuntimeError(f'{rec}: invalid ECG std')
            z=np.clip((ecg-mu)/sd,-4.0,4.0).astype(np.float32).reshape(ne,EPOCH_SAMPLES)
            for start in range(0,len(items),args.batch_size):
                batch=items[start:start+args.batch_size]
                local=np.asarray([x[0] for x in batch],dtype=np.int64)
                eps=np.asarray([x[1] for x in batch],dtype=np.int64)
                if np.any(eps<0) or np.any(eps>=ne): raise RuntimeError(f'{rec}: UID epoch outside Stage02 range')
                x=torch.from_numpy(z[eps,None,:]).to(device)
                qx=torch.from_numpy(sel_q[local]).to(device)
                cx=torch.from_numpy(sel_c[local]).to(device)
                logits,_=model(x,qx,cx)
                probs[local]=torch.softmax(logits,dim=1)[:,1].cpu().numpy().astype(np.float64)
            print(f'{rec}: {len(items)} rows')
    if not np.isfinite(probs).all(): raise RuntimeError('Inference produced non-finite probabilities.')

    out=Path(args.output).expanduser()
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); header=['uid','probability','prediction','threshold']
        if y is not None: header.append('y_learn')
        w.writerow(header)
        for j,(uid,p) in enumerate(zip(sel_uids,probs)):
            row=[uid,f'{p:.17g}',int(p>=threshold),f'{threshold:.17g}']
            if y is not None: row.append(int(y[selected[j]]))
            w.writerow(row)
    print(f'Wrote {len(probs)} rows -> {out}')
    print(f'Checkpoint: {model_path.relative_to(ROOT)}')
    print(f'Operating threshold: {threshold:.17g} (source: learning OOF only unless overridden)')
    print('Official-x labels read: NO' if args.split=='official-x' else 'Learning split requested; y_learn is available.')

    if args.compare_reference:
        r=np.load(ref_path,allow_pickle=False)
        ru=np.asarray(r['test_uids' if args.split=='official-x' else 'learn_uids']).astype(str)
        rp=np.asarray(r[ref_key],dtype=np.float64)
        if not np.array_equal(ru,uids): raise RuntimeError('Reference prediction UID alignment mismatch.')
        expected=rp[selected]
        diff=np.abs(probs-expected)
        mx=float(diff.max()); mean=float(diff.mean())
        print(f'Reference comparison: max_abs={mx:.9g} mean_abs={mean:.9g} tolerance={args.tolerance:g}')
        if mx>args.tolerance:
            raise SystemExit('REFERENCE COMPARISON FAILED')
        print('REFERENCE COMPARISON PASS')

if __name__=='__main__': main()
