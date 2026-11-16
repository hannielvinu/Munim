"""Reproduce the complete OFFLINE package from repository root after installing dependencies."""
import os,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    os.chdir(ROOT)
    def run(*args): subprocess.run(list(args),check=True,cwd=ROOT)
    run(sys.executable,'-m','arena.tune')
    npm='npm.cmd' if os.name=='nt' else 'npm'
    run(npm,'--prefix','web','ci'); run(npm,'--prefix','web','run','build')
    server=None
    try:
        try: urllib.request.urlopen('http://127.0.0.1:8000/api/results',timeout=3).close()
        except Exception:
            server=subprocess.Popen([sys.executable,'-m','uvicorn','api.main:app','--host','127.0.0.1','--port','8000'],cwd=ROOT)
            for _ in range(30):
                try: urllib.request.urlopen('http://127.0.0.1:8000/api/results',timeout=2).close(); break
                except Exception: time.sleep(1)
            else: raise RuntimeError('Local server failed to start')
        run(sys.executable,'scripts/e2e.py')
        run(sys.executable,'scripts/make_video.py')
        run(sys.executable,'scripts/build_submission.py')
        run(sys.executable,'scripts/package_submission.py')
        run(sys.executable,'submission/check.py')
        run(sys.executable,'scripts/package_submission.py')
    finally:
        if server: server.terminate(); server.wait(timeout=10)
if __name__=='__main__': main()
