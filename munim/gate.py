from munim.models import Offer
class Gate:
    def __init__(self, store): self.store=store
    def floor_price(self, item, qty=1): return self.store.floor_price(item,qty)
    def check_offer(self, offer):
        try:
            if not isinstance(offer,Offer):
                data=dict(offer); data['lines']=tuple(data['lines']); offer=Offer.model_validate(data)
            reasons, seen = [], set()
            if not offer.lines: reasons.append('Empty offer')
            for line in offer.lines:
                if line.item in seen: reasons.append('Duplicate item')
                seen.add(line.item); i=self.store.items.get(line.item)
                if i is None: reasons.append('Unknown item'); continue
                if line.qty>i.stock: reasons.append('Insufficient stock')
                if line.unit_price<self.floor_price(line.item,line.qty): reasons.append('Below policy floor')
                if line.unit_price>i.list_price: reasons.append('Above list price')
            if offer.total!=sum(l.qty*l.unit_price for l in offer.lines): reasons.append('Inconsistent total')
            return not reasons,reasons
        except (ValueError,TypeError,KeyError): return False,['Invalid offer schema']

