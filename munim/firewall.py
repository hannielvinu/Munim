import re
from decimal import Decimal
from munim.models import Commitment
from munim.logging import log
PRESSURE=re.compile(r'competitor|other shop|budget|authority|manager|friend|urgent|hurry|guilt|family|leave|ignore|rules|cost|floor|set price|system|developer|dusri dukan|sasta|majboori|jaldi|dost|reveal',re.I)

def parse(message,store,session='local',write_log=True):
    if not isinstance(message,str): raise ValueError('Message must be text')
    needs,pressure,facts,safe={},[],[],[]
    counter,accept=None,False
    for part in re.split(r'[;\n!?]+|\.(?!\d)',message):
        part=part.strip()
        if not part: continue
        if PRESSURE.search(part):
            pressure.append(part)
            if write_log: log('claim_ledger.jsonl',{'session':session,'source':store.source,'pressure':part,'classification':'injection' if re.search('ignore|rules|cost|floor|system|set price',part,re.I) else 'budget' if 'budget' in part.lower() else 'pressure'})
            continue
        safe.append(part)
        for item,qty in re.findall(r'\b([a-z]+\d{2})\s*(?:x|qty\s*)\s*(\d+)\b',part.lower()): needs[item]=int(qty)
        match=re.fullmatch(r'(?:my offer|i offer|counter|mera offer)\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d{1,2})?)',part,re.I)
        if match: counter=int(Decimal(match[1])*100)
        if re.fullmatch(r'i accept|accept|manzoor|haan',part,re.I): accept=True
        match=re.fullmatch(r'(price|stock)\s+([a-z]+\d{2})(?:\s+(\d+))?',part,re.I)
        if match:
            kind,key,claimed=match.groups(); i=store.items.get(key.lower())
            if i:
                actual=i.stock if kind.lower()=='stock' else i.list_price
                facts.append({'item':i.id,'kind':kind.lower(),'actual':actual,'claimed':int(claimed) if claimed else None,'verified':claimed is None or int(claimed)==actual})
    return {'facts':facts,'commitments':Commitment(needs=needs,counter=counter,accept=accept).model_dump(),'pressure':pressure,'clean_message':'; '.join(safe)}

