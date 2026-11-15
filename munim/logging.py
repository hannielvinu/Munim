import json, threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCK=threading.Lock()
def log(name,data):
    path=ROOT/'outputs'/name; path.parent.mkdir(parents=True,exist_ok=True)
    with LOCK, path.open('a',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False)+'\n')

