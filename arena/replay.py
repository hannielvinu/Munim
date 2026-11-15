import json,sys
from munim.agent import Agent
from munim.logging import ROOT
def replay(record):
    a=Agent(brain_name=record['brain'],config=record['config'],session='replay-'+record['id'])
    rows=[]
    for t in record['turns']:
        clean=t['response'].get('firewall',{}).get('clean_message','')
        result=a.respond(clean)
        original=t['response'].get('move'); repeated=result.get('move')
        rows.append({'original_buyer':t['buyer'],'clean_buyer':clean,'original':original,'replayed':repeated,'identical':original==repeated})
    return {'id':record['id'],'persona':record['persona'],'source':record['source'],'rows':rows,'identical':all(t['identical'] for t in rows)}
def run_replays(records):
    results=[replay(r) for r in records if r['persona'] in ('manipulator','prompt-injector')]
    total=sum(len(r['rows']) for r in results); same=sum(t['identical'] for r in results for t in r['rows'])
    out={'source':records[0]['source'],'negotiations':len(results),'offers_compared':total,'identical_offers':same,'identical_pct':100*same/total,'replays':results}
    (ROOT/'outputs/claim_invariance.json').write_text(json.dumps(out,indent=2))
    (ROOT/f"outputs/{records[0]['source']}_claim_invariance.json").write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':
    data=json.loads((ROOT/'outputs/claim_invariance.json').read_text())
    r=next(r for r in data['replays'] if r['id']==sys.argv[1])
    for row in r['rows']: print(f"{row['original_buyer']:<90} | {row['clean_buyer']}\n{row['original']} | {row['replayed']}\n")

