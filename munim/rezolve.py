import os
from munim.adapters.rezolve_adapter import LiveClient
from munim.logging import log
from munim.voice import template

class Rezolve:
    def __init__(self,store,session='local'):
        self.store=store; self.session=session
        self.mode=os.getenv('REZOLVE_MODE','mock').upper()
        if self.mode not in ('MOCK','LIVE'): raise ValueError('Unknown Rezolve mode')
        self.client=LiveClient() if self.mode=='LIVE' else None
        self.index={k:i.model_dump() for k,i in store.items.items()}
        self.index['policy']=store.policy
        if self.client:
            # Ingestion failure is visible, never reported as a successful live index.
            try: self.client.call('index',{'documents':self.index})
            except Exception: log('retrieval_log.jsonl',{'session':session,'mode':'LIVE','path':'local_fallback','operation':'index','ok':False})
    def lookup(self,key):
        path='mock_local'; data=self.index[key]
        if self.client:
            try:
                result=self.client.call('lookup',{'query':key})
                if result!=data: raise ValueError('Retrieved data does not match source of truth')
                data=result; path='managed'
            except Exception: path='local_fallback'
        log('retrieval_log.jsonl',{'session':self.session,'source':self.store.source,'mode':self.mode,'key':key,'path':path})
        return data
    def verify(self,move,text,facts,language='en'):
        evidence=[]; ok=True
        for line in move.offer.lines if move.offer else []:
            row=self.lookup(line.item)
            evidence.extend([{'action':'price_lookup','item':line.item,'value':row['list_price']},{'action':'stock_check','item':line.item,'value':row['stock']},{'action':'floor_check','item':line.item,'value':self.store.floor_price(line.item)}])
            ok=ok and self.store.floor_price(line.item)<=line.unit_price<=row['list_price'] and 0<line.qty<=row['stock']
        if move.offer: ok=ok and move.offer.total==sum(l.qty*l.unit_price for l in move.offer.lines)
        fact_text=' '.join(f"Catalogue {f['kind']} for {f['item']}: {f['actual']}"+(' paise.' if f['kind']=='price' else ' units.') for f in facts)
        for fact in facts:
            row=self.lookup(fact['item']); actual=row['stock'] if fact['kind']=='stock' else row['list_price']
            ok=ok and fact['actual']==actual
            evidence.append({'action':fact['kind']+'_lookup','item':fact['item'],'value':actual})
        ok=ok and text==template(move,language)+(' '+fact_text if fact_text else '')
        if self.client:
            try: ok=ok and self.client.call('verify',{'claims':move.model_dump(mode='json'),'trace':evidence,'text':text}) is True
            except Exception: ok=False
        verdict={'mode':self.mode,'ok':bool(ok),'evidence':evidence,'source':self.store.source,'session':self.session}
        log('traceware_log.jsonl',verdict)
        return verdict

