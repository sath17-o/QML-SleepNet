from __future__ import annotations
import importlib, platform, sys
mods=['numpy','pandas','scipy','sklearn','matplotlib','torch','pennylane','wfdb']
print('Python:',sys.version.split()[0],platform.platform())
failed=[]
for m in mods:
    try:
        x=importlib.import_module(m); print(f'{m:12s}',getattr(x,'__version__','installed'))
    except Exception as e:
        failed.append((m,str(e))); print(f'{m:12s} MISSING ({e})')
if failed:
    print('\nFull research execution dependencies are incomplete. Install requirements.txt.')
else:
    print('\nFull research execution environment: core imports PASS')
print('Note: verify mode itself uses only the Python standard library.')
