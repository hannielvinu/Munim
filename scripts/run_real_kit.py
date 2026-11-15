import os,subprocess,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
def main():
    os.environ['MUNIM_KIT']='official'
    from munim.adapters.store_adapter import kit_path
    from munim.store import Store
    store=Store(); kit=kit_path()
    config=ROOT/'config/official_harness.json'
    if not config.exists(): raise SystemExit('Configure config/official_harness.json with documented evaluate_args and seller adapter first; see docs/SWAP_IN_REAL_KIT.md')
    args=json.loads(config.read_text())['evaluate_args']
    out=ROOT/'outputs/dev_set_official'; out.mkdir(parents=True,exist_ok=True)
    result=subprocess.run([sys.executable,str(kit/'evaluate.py'),*args],cwd=ROOT,text=True,capture_output=True)
    (out/'OFFICIAL_evaluator_stdout.txt').write_text(result.stdout,encoding='utf-8')
    (out/'OFFICIAL_evaluator_stderr.txt').write_text(result.stderr,encoding='utf-8')
    if result.returncode: raise SystemExit(result.returncode)
    from arena.run import run
    from arena.replay import run_replays
    summary,records=run(200,7); run_replays(records)
    # OFFICIAL means catalogue provenance; the arena remains our own evaluation.
    summary['official_evaluator_note']='See outputs/dev_set_official; arena scoring is Munim-defined, not automatically official scoring.'
    (ROOT/'outputs/summary.json').write_text(json.dumps(summary,indent=2))
    subprocess.run([sys.executable,'scripts/build_submission.py'],check=True,cwd=ROOT)
if __name__=='__main__': main()

