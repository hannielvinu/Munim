import json,uuid,threading
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from munim.agent import Agent
from munim.llm import LLM
from munim.store import Store
from munim.logging import ROOT
from arena.personas import PERSONAS,message
app=FastAPI(title='Munim • SIMULATED shop')
sessions={}; lock=threading.Lock()
def read(name):
    path=ROOT/'outputs'/name
    if not path.exists(): raise HTTPException(503,'Results are not ready. Run python -m arena.tune.')
    return json.loads(path.read_text())
class NewSession(BaseModel):
    persona:str='manipulator'
    brain:str='ladder'
    language:str='en'
class Turn(BaseModel):
    message:str|None=Field(default=None,max_length=3000)
@app.get('/api/catalogue')
def catalogue():
    s=Store()
    return {'source':s.source,'items':[dict(i.model_dump(),floor=s.floor_price(i.id)) for i in s.items.values()],'policy':s.policy}
@app.get('/api/results')
def results(): return read('summary.json')
@app.get('/api/replays')
def replays(): return read('claim_invariance.json')
@app.get('/api/khata')
def khata():
    s=Store(); records=read(s.source+'_transcripts.json')
    deals=[{'id':r['id'],'persona':r['persona'],'brain':r['brain'],'offer':r['turns'][-1]['response']['move']['offer']} for r in records if r['turns'][-1]['response'].get('move',{}).get('kind')=='accept']
    ledger=ROOT/'outputs/claim_ledger.jsonl'; counts={}
    for line in ledger.read_text(encoding='utf-8').splitlines() if ledger.exists() else []:
        c=json.loads(line).get('classification','pressure'); counts[c]=counts.get(c,0)+1
    return {'source':s.source,'deals':deals,'tricks':counts,'scope':'Cumulative local ledger, including tests and replays'}
@app.post('/api/sessions')
def new_session(body:NewSession):
    if body.persona not in PERSONAS or body.brain not in ('ladder','baseline') or body.language not in ('en','hi'): raise HTTPException(422,'Unknown option')
    with lock:
        if len(sessions)>500: sessions.pop(next(iter(sessions)))
        sid=uuid.uuid4().hex; llm=LLM(sid)
        a=Agent(brain_name=body.brain,session=sid,language=body.language,llm=llm if llm.provider!='none' else None)
        sessions[sid]={'agent':a,'persona':body.persona,'history':[],'llm':llm}
    return {'id':sid,'source':a.store.source,'mode':'OFFLINE' if llm.provider=='none' else 'LLM'}
@app.post('/api/sessions/{sid}/turn')
def turn(sid:str,body:Turn):
    with lock:
        session=sessions.get(sid)
        if not session: raise HTTPException(404,'Session expired. Start a new negotiation.')
        a=session['agent']
        if a.closed: raise HTTPException(409,'Negotiation is closed. Start a new one.')
        msg=body.message if body.message is not None else message(session['persona'],a.round+1,a.store.items,session['history'],7,session['llm'])
        result=a.respond(msg)
        # Debug diagnostics belong only to shopkeeper panel, never the seller text.
        counter=result.get('firewall',{}).get('commitments',{}).get('counter')
        result['counter_check']=None
        if counter is not None and a.previous and len(a.previous.lines)==1:
            l=a.previous.lines[0]; unit=counter//l.qty
            ok,reasons=a.gate.check_offer({'lines':[{'item':l.item,'qty':l.qty,'unit_price':unit}],'total':unit*l.qty})
            result['counter_check']={'ok':ok,'reasons':reasons}
        if a.previous:
            profit=sum((l.unit_price-a.store.items[l.item].cost)*l.qty for l in a.previous.lines)
            result['margin_paise']=profit
            result['margin_pct']=100*profit/a.previous.total
        session['history'].append({'buyer':msg,'response':result})
        return {'buyer':msg,'response':result}
web=ROOT/'web/dist'
if web.exists():
    app.mount('/assets',StaticFiles(directory=web/'assets'),name='assets')
    @app.get('/{path:path}')
    def index(path:str): return FileResponse(web/'index.html')

