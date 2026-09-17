from __future__ import annotations
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXEC=json.loads((ROOT/'config/execution_manifest.json').read_text(encoding='utf-8'))

def run(cmd): subprocess.run(cmd,check=True)

def verify_local():
    run([sys.executable,str(ROOT/'scripts/check_guide_alignment.py')])
    run([sys.executable,str(ROOT/'scripts/verify_artifacts.py')])
    run([sys.executable,str(ROOT/'scripts/verify_results.py')])
    run([sys.executable,str(ROOT/'scripts/audit_notebooks.py')])
    # Repository tests are part of verification and must not be silently skipped.
    try:
        import pytest  # noqa
    except Exception as exc:
        raise SystemExit('pytest is required for verify mode. Install requirements-verify.txt first.') from exc
    run([sys.executable,'-m','pytest','-q',str(ROOT/'tests')])

def missing(workspace, rels): return [rel for rel in rels if not (workspace/rel).exists()]

def patch_notebook(src,dst,workspace):
    nb=json.loads(src.read_text(encoding='utf-8'))
    ws=str(workspace).replace('\\','\\\\')
    for cell in nb.get('cells',[]):
        if cell.get('cell_type')!='code': continue
        source=''.join(cell.get('source',[])); lines=[]
        for line in source.splitlines(True):
            stripped=line.strip()
            if stripped.startswith('!pip ') or stripped.startswith('%pip '): continue
            if stripped.startswith('from google.colab import drive'): continue
            if stripped.startswith('drive.mount('): continue
            lines.append(line)
        source=''.join(lines).replace('/content/drive/MyDrive/QML_SleepNet',ws)
        cell['source']=source.splitlines(True); cell['outputs']=[]; cell['execution_count']=None
    dst.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')

def execute_notebook(src,workspace,executed_dir):
    executed_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='qml_sleepnet_nb_') as td:
        patched=Path(td)/src.name; patch_notebook(src,patched,workspace)
        cmd=[sys.executable,'-m','jupyter','nbconvert','--to','notebook','--execute',str(patched),'--ExecutePreprocessor.timeout=-1','--ExecutePreprocessor.allow_errors=False','--output',src.stem+'.executed.ipynb','--output-dir',str(executed_dir)]
        print('  executing:',src.name,flush=True); run(cmd)

def run_chain(key,workspace,resume):
    executed=workspace/'outputs'/'github_submission_executed_notebooks'
    for stage in EXEC[key]:
        outputs=[workspace/p for p in stage['produces']]
        if resume and outputs and all(p.exists() for p in outputs):
            print(f"[RESUME] {stage['id']} {stage['name']} — output contract already present"); continue
        miss=missing(workspace,stage['requires'])
        if miss:
            details='\n'.join('  - '+str(workspace/x) for x in miss)
            raise SystemExit(f"Cannot run {stage['id']} {stage['name']}: required frozen/source artifacts are missing.\n{details}\nThe runner fails closed and will not substitute another experiment.")
        # Stage03's frozen notebook discovers a reusable feature cache dynamically.
        # Reproduce that selection rule and fail if today's workspace would select
        # a different cache than the one recorded by the frozen Stage03 manifest.
        if stage.get('source_lock'):
            lock=stage['source_lock']; required=lock['required_files']; candidates=[]
            def valid_bank(d): return d.is_dir() and all((d/x).exists() for x in required)
            for rel in lock['candidate_roots']:
                r=workspace/rel
                if r.exists():
                    if valid_bank(r): candidates.append(r)
                    for d in r.rglob('*'):
                        if valid_bank(d): candidates.append(d)
            if not candidates:
                raise SystemExit('Stage03 source-lock failure: no valid frozen feature-cache candidate found.')
            candidates=sorted(set(candidates),key=lambda d:((d/'feature_values_float32.npz').stat().st_size,(d/'feature_values_float32.npz').stat().st_mtime),reverse=True)
            chosen=candidates[0].resolve(); frozen=(workspace/lock['frozen_selected_directory']).resolve()
            if chosen!=frozen:
                raise SystemExit(
                    'Stage03 source-lock failure: the unmodified frozen notebook would select a different label-free cache today.\n'
                    f'  frozen selected: {frozen}\n  would select now: {chosen}\n'
                    'Refusing to recompute a scientifically different Stage03. Use the frozen outputs or restore the frozen source-cache state.'
                )
        src=ROOT/stage['notebook']
        if not src.is_file(): raise SystemExit(f'Submission notebook missing: {src}')
        print(f"\n[{stage['id']}] {stage['name']}"); execute_notebook(src,workspace,executed)
        absent=[p for p in outputs if not p.exists()]
        if absent: raise SystemExit('Stage finished without declared output contract:\n'+'\n'.join('  - '+str(p) for p in absent))
        print('  output contract: PASS')

def main():
    ap=argparse.ArgumentParser(description='QML-SleepNet guide-locked reviewer runner')
    ap.add_argument('--mode',choices=['verify','inference','guide-replay','guide','promoted-evidence','full'],default='verify')
    ap.add_argument('--workspace',default='external_workspace/QML_SleepNet',help='Prepared original QML_SleepNet workspace for research replay modes')
    ap.add_argument('--stage02-dir',default='',help='Stage02 preprocessed record directory for frozen inference')
    ap.add_argument('--split',choices=['official-x','learn'],default='official-x')
    ap.add_argument('--output',default='outputs/frozen_stage06_predictions.csv')
    ap.add_argument('--batch-size',type=int,default=128)
    ap.add_argument('--device',choices=['auto','cpu','cuda'],default='auto')
    ap.add_argument('--records',default='')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--compare-reference',action='store_true')
    ap.add_argument('--tolerance',type=float,default=1e-4)
    ap.add_argument('--no-resume',action='store_true')
    args=ap.parse_args()

    if args.mode=='verify':
        print('QML-SleepNet guide-locked verification (no training, no dataset labels)')
        verify_local(); print('\nVERIFY MODE COMPLETE'); return
    if args.mode=='inference':
        if not args.stage02_dir: raise SystemExit('--stage02-dir is required for --mode inference')
        cmd=[sys.executable,str(ROOT/'scripts/run_frozen_stage06.py'),'--stage02-dir',args.stage02_dir,'--split',args.split,'--output',args.output,'--batch-size',str(args.batch_size),'--device',args.device,'--tolerance',str(args.tolerance)]
        if args.records: cmd += ['--records',args.records]
        if args.limit: cmd += ['--limit',str(args.limit)]
        if args.compare_reference: cmd += ['--compare-reference']
        run(cmd); return

    workspace=Path(args.workspace).expanduser().resolve()
    if not workspace.is_dir(): raise SystemExit(f'Workspace not found: {workspace}\nSee docs/FULL_REPRODUCTION.md')
    for top in ['data','outputs']:
        if not (workspace/top).exists(): raise SystemExit(f'Workspace contract missing: {workspace/top}')
    resume=not args.no_resume
    mode='guide-replay' if args.mode=='guide' else args.mode
    if mode in ('guide-replay','full'): run_chain('guide_replay_chain',workspace,resume)
    if mode in ('promoted-evidence','full'): run_chain('promoted_evidence_chain',workspace,resume)
    print(f'\n{mode.upper()} MODE COMPLETE')

if __name__=='__main__': main()
