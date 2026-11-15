import os,time
import httpx,yaml
from munim.logging import ROOT,log

class LiveClient:
    def __init__(self):
        self.config=yaml.safe_load((ROOT/'config/rezolve.yaml').read_text())
        self.base=os.getenv('REZOLVE_BASE_URL',''); self.key=os.getenv('REZOLVE_API_KEY',''); self.credits=0
    def call(self,operation,data):
        op=self.config['operations'][operation]
        if not self.key or not self.base.startswith('https://') or 'TODO' in str(op):
            raise RuntimeError('Live Rezolve configuration incomplete; consult official docs')
        def expand(v):
            if isinstance(v,str) and v.startswith('$'): return data[v[1:]]
            if isinstance(v,dict): return {k:expand(x) for k,x in v.items()}
            if isinstance(v,list): return [expand(x) for x in v]
            return v
        for attempt in range(self.config['retries']+1):
            if self.credits>=self.config['credit_limit']: raise RuntimeError('Credit limit reached')
            self.credits+=1
            try:
                r=httpx.post(self.base.rstrip('/')+'/'+op['path'].lstrip('/'),json=expand(op['request_template']),headers={self.config['auth_header']:self.config['auth_prefix']+self.key},timeout=self.config['timeout_seconds'])
                r.raise_for_status(); result=r.json()
                for part in op['response_path'].split('.'): result=result[part]
                log('rezolve_calls.jsonl',{'mode':'LIVE','operation':operation,'attempt':attempt,'credits':self.credits,'ok':True})
                return result
            except (httpx.HTTPError,ValueError,KeyError):
                log('rezolve_calls.jsonl',{'mode':'LIVE','operation':operation,'attempt':attempt,'credits':self.credits,'ok':False})
                if attempt==self.config['retries']: raise
                time.sleep(.2*2**attempt)

