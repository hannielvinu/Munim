import argparse,json,statistics
from pathlib import Path
from decimal import Decimal
from munim.agent import Agent
from munim.store import Store
from munim.llm import LLM
from munim.ladder import settings
from munim.logging import ROOT
from arena.personas import PERSONAS,message
from arena.checker import check
def simulate(persona,seed,brain,config=None,prefix='arena'):
    sid=f'{prefix}-{brain}-{seed:04d}'; llm=LLM(sid)
    a=Agent(brain_name=brain,config=config,session=sid,llm=llm if llm.provider!='none' else None); turns=[]
    for turn in range(1,11):
        msg=message(persona,turn,a.store.items,turns,seed,llm)
        result=a.respond(msg); turns.append({'buyer':msg,'response':result})
        if result.get('closed'): break
    return {'id':sid,'source':a.store.source,'mode':'OFFLINE' if llm.provider=='none' else 'LLM','brain':brain,'persona':persona,'seed':seed,'turns':turns,'usage':llm.usage,'config':config or settings()}
def metrics(records):
    s=Store(); deals=violations=truths=claims=deadlocks=profit=list_profit=0
    tokens=0; costs=[]; unknown=False
    for r in records:
        final=r['turns'][-1]['response']; move=final.get('move',{})
        if move.get('kind')=='accept':
            deals+=1
            for l in move['offer']['lines']:
                i=s.items[l['item']]; profit+=(l['unit_price']-i.cost)*l['qty']; list_profit+=(i.list_price-i.cost)*l['qty']
        deadlocks+=not final.get('closed',False)
        for t in r['turns']:
            v,ok=check(t['response'],s); violations+=v; truths+=ok; claims+=1
        for u in r['usage']:
            tokens+=u['input_tokens']+u['output_tokens']
            if u['cost_inr'] is None: unknown=True
            else: costs.append(Decimal(u['cost_inr']))
    n=len(records)
    m={'n':n,'deals':deals,'deal_rate':deals/n,'margin_kept':profit/list_profit if list_profit else 0,'policy_violations':violations,'violation_rate':violations/claims,'deadlock_rate':deadlocks/n,'truthfulness':truths/claims,'average_rounds':statistics.mean(len(r['turns']) for r in records),'tokens':tokens,'tokens_per_negotiation':tokens/n,'rupees_per_negotiation':None if unknown else str(sum(costs,Decimal(0))/n),'rounds_distribution':{str(k):sum(len(r['turns'])==k for r in records) for k in range(1,11)}}
    m['score']=.55*m['deal_rate']+.35*m['margin_kept']+.10*m['truthfulness']-2*m['violation_rate']-m['deadlock_rate']
    return m
def run(n=200,seed=7,out=None,config=None):
    records=[simulate(PERSONAS[j%6],seed+j,b,config) for b in ('ladder','baseline') for j in range(n)]
    summary={'source':Store().source,'mode':records[0]['mode'],'rezolve':'MOCK' if not __import__('os').getenv('REZOLVE_MODE') else __import__('os').getenv('REZOLVE_MODE').upper(),'seed':seed,'n_per_brain':n,'total_negotiations':len(records),'brains':{}}
    for b in ('ladder','baseline'):
        group=[r for r in records if r['brain']==b]
        summary['brains'][b]=metrics(group)
        summary['brains'][b]['personas']={p:metrics([r for r in group if r['persona']==p]) for p in PERSONAS if any(r['persona']==p for r in group)}
    summary['selected_brain']=max(summary['brains'],key=lambda b:summary['brains'][b]['score'])
    dest=Path(out) if out else ROOT/'outputs'
    if records[0]['mode']=='LLM' and out is None: dest=dest/'llm'
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'summary.json').write_text(json.dumps(summary,indent=2))
    (dest/f"{summary['source']}_summary.json").write_text(json.dumps(summary,indent=2))
    (dest/'summary.md').write_text('# '+summary['source']+' / '+summary['mode']+' results\n\n'+json.dumps(summary,indent=2))
    (dest/f"{summary['source']}_transcripts.json").write_text(json.dumps(records,indent=2))
    return summary,records
def run_dev():
    records=[]
    for b in ('ladder','baseline'):
        for j,p in enumerate(['cooperative','hard bargainer','manipulator']*10):
            records.append(simulate(p,j,b,prefix='dev'))
    dest=ROOT/'outputs/dev_set'; dest.mkdir(parents=True,exist_ok=True)
    (dest/'SIMULATED_results.json').write_text(json.dumps({'source':'SIMULATED','brains':{b:metrics([r for r in records if r['brain']==b]) for b in ('ladder','baseline')}},indent=2))
    (dest/'SIMULATED_transcripts.json').write_text(json.dumps(records,indent=2))
    print('SIMULATED development set: 60 negotiations saved')
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--n',type=int,default=200); p.add_argument('--seed',type=int,default=7)
    args=p.parse_args()
    if args.n<6: p.error('--n must be at least 6')
    summary,_=run(args.n,args.seed); print(json.dumps(summary,indent=2))

