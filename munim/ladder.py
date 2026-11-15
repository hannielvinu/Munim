from pathlib import Path
import yaml
from munim.models import Line,Offer
def settings(): return yaml.safe_load((Path(__file__).resolve().parents[1]/'config.yaml').read_text())
def offer_for(store,needs,config,opening=False,discount_override=None):
    lines=[]
    for key,qty in sorted(needs.items()):
        i=store.items[key]
        discount=max(d for q,d in config['quantity_tiers'].items() if qty>=int(q))
        if len(needs)>1: discount+=config['bundle_discount_bps']
        if discount_override is not None: discount=discount_override
        price=i.list_price if opening else max(store.floor_price(key,qty)+config['safety_buffer_paise'],(i.list_price*(10000-discount)+9999)//10000)
        lines.append(Line(item=key,qty=qty,unit_price=price))
    return Offer(lines=tuple(lines),total=sum(l.qty*l.unit_price for l in lines))
def next_hint(needs):
    if any(q<3 for q in needs.values()): return 'Commit to three units of an item to unlock the quantity tier.'
    if any(q<6 for q in needs.values()): return 'Commit to six units of an item to unlock the next quantity tier.'
    if len(needs)<2: return 'Add another item to unlock the bundle tier.'
    return 'You qualify for the best available commitment tier.'

