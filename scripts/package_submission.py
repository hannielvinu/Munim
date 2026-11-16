import subprocess,zipfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'submission'
def package():
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    source=S/'code/Munim_source.zip'; source.parent.mkdir(exist_ok=True)
    # Include current uncommitted authoring scripts too; never include private or generated bulky content.
    paths=set(tracked)
    for folder in ['munim','arena','api','web','scripts','tests','docs','config','standin_kit','starter']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and not any(x in p.parts for x in ['node_modules','__pycache__','dist','.pytest_cache']): paths.add(p.relative_to(ROOT).as_posix())
    paths.update(['submission/check.py','submission/README_SUBMISSION.md'])
    with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(paths):
            p=ROOT/name
            if not p.is_file() or name.startswith(('submission/','outputs/','.venv/','.git/','tmp/')) and name not in ('submission/check.py','submission/README_SUBMISSION.md'): continue
            if p.name.startswith('.env') and p.name!='.env.example': continue
            if p.suffix in ('.pyc','.tsbuildinfo') or any(x in p.parts for x in ['node_modules','__pycache__','dist']): continue
            z.write(p,name)
    target=ROOT/'Munim_Round1_TM-394CDC172A3.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(S.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts: z.write(p,p.relative_to(ROOT))
    print(f'Packaged {target.name}: {target.stat().st_size} bytes')
if __name__=='__main__': package()
