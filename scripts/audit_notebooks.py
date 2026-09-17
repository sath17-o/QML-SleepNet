from __future__ import annotations
import ast, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = sorted((ROOT/'notebooks').rglob('*.ipynb'))
errors=[]; code_cells=0
for p in paths:
    try:
        nb=json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        errors.append(f'{p.relative_to(ROOT)}: invalid JSON: {e}')
        continue
    for i,c in enumerate(nb.get('cells',[])):
        if c.get('cell_type')!='code': continue
        src=''.join(c.get('source',[]))
        # IPython/Colab magics and shell commands are valid notebook syntax but not Python AST.
        cleaned=[]
        for line in src.splitlines():
            s=line.lstrip()
            if s.startswith(('!','%')): continue
            cleaned.append(line)
        code='\n'.join(cleaned)
        try:
            compile(code, f'{p.name}:cell{i}', 'exec')
            code_cells+=1
        except SyntaxError as e:
            errors.append(f'{p.relative_to(ROOT)} cell {i}: {e.msg} line {e.lineno}')
if errors:
    raise SystemExit('Notebook audit FAILED:\n'+'\n'.join(errors))
print(f'Notebook audit PASSED: {len(paths)} notebooks, {code_cells} Python code cells compiled')
