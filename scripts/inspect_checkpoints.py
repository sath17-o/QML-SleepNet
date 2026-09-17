from __future__ import annotations
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    try:
        import torch
    except Exception as e:
        raise SystemExit(f'PyTorch required for checkpoint inspection: {e}')
    man=json.loads((ROOT/'pretrained/ARTIFACT_MANIFEST.json').read_text())
    pts=[ROOT/a['file'] for a in man['artifacts'] if a['file'].endswith('.pt')]
    for p in pts:
        try: ck=torch.load(p,map_location='cpu',weights_only=True)
        except TypeError: ck=torch.load(p,map_location='cpu')
        sd=ck.get('state_dict')
        if not isinstance(sd,dict) or not sd: raise SystemExit(f'{p}: state_dict missing')
        n=sum(int(v.numel()) for v in sd.values() if hasattr(v,'numel'))
        meta={k:v for k,v in ck.items() if k!='state_dict'}
        print(p.relative_to(ROOT), 'params_or_buffers=',n, 'meta=',meta)
    # Structural locks on the actual tensor files, not only manifests.
    b=torch.load(ROOT/'pretrained/bridge/bridge128to8_model.pt',map_location='cpu',weights_only=True)
    assert tuple(b['state_dict']['fc1.weight'].shape)==(64,128)
    assert tuple(b['state_dict']['fc2.weight'].shape)==(32,64)
    assert tuple(b['state_dict']['fc3.weight'].shape)==(8,32)
    v=torch.load(ROOT/'pretrained/qml/final_vqc_angle_rx.pt',map_location='cpu',weights_only=True)
    assert tuple(v['state_dict']['qweights'].shape)==(4,8,3)
    s=torch.load(ROOT/'pretrained/stage06/qml_sleepnet_final_guide_corrected.pt',map_location='cpu',weights_only=True)
    assert s['task']=='binary Apnea vs Normal' and s['official_x_labels_used'] is False
    assert tuple(s['state_dict']['fusion256.weight'].shape)==(256,536)
    assert tuple(s['state_dict']['out.weight'].shape)==(2,64)
    print('CHECKPOINT STRUCTURE PASS')

if __name__=='__main__': main()
