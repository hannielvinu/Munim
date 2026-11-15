from munim.adapters.store_adapter import load_catalogue
class Store:
    def __init__(self):
        self.items, self.policy, self.source = load_catalogue()
    def floor_price(self, item, qty=1):
        if type(qty) is not int or qty <= 0: raise ValueError('Quantity must be positive integer')
        i = self.items[item]; p = self.policy['categories'][i.category]
        return max((i.cost*(10000+p['min_margin_bps'])+9999)//10000,
                   (i.list_price*(10000-p['max_discount_bps'])+9999)//10000)

