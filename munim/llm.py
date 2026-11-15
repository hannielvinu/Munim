import os,json
from decimal import Decimal
import httpx
from dotenv import load_dotenv
from munim.logging import log
load_dotenv()
class LLM:
    def __init__(self,session):
        self.provider=os.getenv('LLM_PROVIDER','none'); self.model=os.getenv('LLM_MODEL',''); self.session=session
        self.usage=[]
        if self.provider not in ('none','openai','anthropic','gemini'): raise ValueError('Unknown LLM provider')
    def __call__(self,prompt):
        p=self.provider
        if p=='none': raise RuntimeError('OFFLINE MODE')
        key=os.getenv(p.upper()+'_API_KEY','')
        if not key or not self.model: raise ValueError('Provider key and model required')
        headers={'Content-Type':'application/json'}
        if p=='openai':
            url='https://api.openai.com/v1/chat/completions'; headers['Authorization']='Bearer '+key
            body={'model':self.model,'messages':[{'role':'user','content':prompt}]}
        elif p=='anthropic':
            url='https://api.anthropic.com/v1/messages'; headers.update({'x-api-key':key,'anthropic-version':'2023-06-01'})
            body={'model':self.model,'max_tokens':256,'messages':[{'role':'user','content':prompt}]}
        else:
            url='https://generativelanguage.googleapis.com/v1beta/models/'+self.model+':generateContent'
            headers['x-goog-api-key']=key; body={'contents':[{'parts':[{'text':prompt}]}]}
        r=httpx.post(url,headers=headers,json=body,timeout=30); r.raise_for_status(); d=r.json()
        if p=='openai':
            text=d['choices'][0]['message']['content']; raw=d['usage']; inp=raw['prompt_tokens']; out=raw['completion_tokens']
        elif p=='anthropic':
            text=d['content'][0]['text']; raw=d['usage']; inp=raw['input_tokens']; out=raw['output_tokens']
        else:
            text=d['candidates'][0]['content']['parts'][0]['text']; raw=d['usageMetadata']; inp=raw['promptTokenCount']; out=raw.get('candidatesTokenCount',0)+raw.get('thoughtsTokenCount',0)
        rates=[os.getenv('LLM_INPUT_INR_PER_MILLION'),os.getenv('LLM_OUTPUT_INR_PER_MILLION')]
        cost=str((Decimal(inp)*Decimal(rates[0])+Decimal(out)*Decimal(rates[1]))/Decimal(1000000)) if all(rates) else None
        usage={'session':self.session,'provider':p,'model':self.model,'input_tokens':inp,'output_tokens':out,'cost_inr':cost,'raw_usage':raw}
        self.usage.append(usage); log('token_usage.jsonl',usage)
        return text

