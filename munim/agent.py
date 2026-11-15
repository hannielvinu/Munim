import uuid
from munim.store import Store
from munim.gate import Gate
from munim.models import State,Commitment,Move
from munim.firewall import parse
from munim.ladder import settings
from munim import brain,baseline_brain,voice

class Agent:
    def __init__(self,brain_name=None,config=None,session=None,language='en',verifier=None,llm=None):
        self.store=Store(); self.gate=Gate(self.store); self.config=config or settings()
        self.brain_name=brain_name or self.config['brain']; self.session=session or uuid.uuid4().hex
        from munim.rezolve import Rezolve
        self.language=language; self.verifier=verifier or Rezolve(self.store,self.session); self.llm=llm
        self.round=0; self.needs={}; self.previous=None; self.previous_needs={}; self.closed=False
    def respond(self,message):
        if self.closed: return {'blocked':True,'error':'Session is closed','closed':True}
        self.round+=1
        fw={'facts':[],'commitments':{},'pressure':[],'clean_message':''}; reasons=[]
        try:
            fw=parse(message,self.store,self.session)
            c=Commitment.model_validate(fw['commitments'])
            if c.needs: self.needs=c.needs
            c=c.model_copy(update={'needs':self.needs.copy()})
            state=State(round=self.round,commitment=c,previous=self.previous,previous_needs=self.previous_needs)
            move=(brain if self.brain_name=='ladder' else baseline_brain).next_move(state,self.store,self.config)
            if move.offer:
                ok,reasons=self.gate.check_offer(move.offer)
                if not ok: raise ValueError('Gate blocked move')
        except Exception:
            move=Move(kind='walk',hint='I cannot safely complete this request.')
        text=voice.render(move,self.language,self.llm)
        facts_text=' '.join(f"Catalogue {f['kind']} for {f['item']}: {f['actual']}"+(' paise.' if f['kind']=='price' else ' units.') for f in fw['facts'])
        if facts_text: text+=' '+facts_text
        verdict={'mode':'LOCAL','ok':True,'evidence':[]}
        if self.verifier:
            verdict=self.verifier.verify(move,text,fw['facts'],self.language)
            if not verdict['ok']:
                self.closed=True
                return {'blocked':True,'closed':True,'error':'Verification unavailable or failed; nothing sent','trace':verdict}
        if move.offer: self.previous=move.offer; self.previous_needs=self.needs.copy()
        self.closed=move.kind in ('accept','walk')
        return {'session':self.session,'source':self.store.source,'round':self.round,'brain':self.brain_name,'move':move.model_dump(mode='json'),'text':text,'firewall':fw,'gate':{'ok':True,'reasons':reasons},'trace':verdict,'closed':self.closed}

