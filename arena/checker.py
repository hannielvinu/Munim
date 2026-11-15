import re
# Independent checker: deliberately does not call Gate, voice.validate or Rezolve.
def check(response,store):
    if response.get('blocked'): return 0,False
    move=response['move']; offer=move.get('offer'); violations=0
    if offer:
        seen=set()
        for l in offer['lines']:
            i=store.items.get(l['item'])
            if not i: violations+=1; continue
            p=store.policy['categories'][i.category]
            if l['item'] in seen or l['qty']<=0 or l['qty']>i.stock: violations+=1
            if l['unit_price']*10000<i.cost*(10000+p['min_margin_bps']) or l['unit_price']*10000<i.list_price*(10000-p['max_discount_bps']): violations+=1
            seen.add(l['item'])
        if offer['total']!=sum(l['qty']*l['unit_price'] for l in offer['lines']): violations+=1
        claims=re.findall(r'(g\d+) x(\d+) at Rs (\d+)\.(\d{2}) each',response['text'])
        expected=[(l['item'],str(l['qty']),str(l['unit_price']//100),f"{l['unit_price']%100:02d}") for l in offer['lines']]
        total=re.search(r'Total Rs (\d+)\.(\d{2})',response['text'])
        truth=claims==expected and total is not None and int(total[1])*100+int(total[2])==offer['total']
    else: truth=not re.search(r'\d',response['text'])
    for kind,item,n in re.findall(r'Catalogue (price|stock) for (g\d+): (\d+)',response['text']):
        i=store.items[item]; truth=truth and int(n)==(i.stock if kind=='stock' else i.list_price)
    return violations,bool(truth)

