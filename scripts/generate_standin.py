import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    dest=ROOT/'standin_kit'; dest.mkdir(exist_ok=True)
    categories={
    'Grains':('Whole wheat atta,Basmati rice,Sona masoori rice,Poha,Rava,Dalia,Maida',1200,1200),
    'Pulses':('Toor dal,Moong dal,Masoor dal,Chana dal,Kabuli chana,Rajma,Urad dal',1500,1000),
    'Oils':('Sunflower oil,Mustard oil,Groundnut oil,Coconut oil,Rice bran oil,Sesame oil,Ghee',800,800),
    'Pantry':('Sugar,Salt,Turmeric,Chilli powder,Cumin,Coriander powder,Jaggery',1800,1500),
    'Beverages':('Assam tea,Filter coffee,Instant coffee,Green tea,Cocoa,Malt drink,Milk powder',2000,1200),
    'Snacks':('Marie biscuits,Glucose biscuits,Cream biscuits,Rusk,Namkeen,Peanuts,Popcorn',2500,1800),
    'Care':('Bath soap,Detergent,Dishwash bar,Toothpaste,Shampoo,Handwash,Floor cleaner',2200,1500)}
    rows=[]; policy={'margin_basis':'cost','discount_basis':'list_price','categories':{}}
    for cat,(names,margin,discount) in categories.items():
        policy['categories'][cat]={'min_margin_bps':margin,'max_discount_bps':discount}
        for name in names.split(','):
            n=len(rows)+1; price=(35+(n*37)%360)*100
            rows.append(dict(id=f'g{n:02}',name=name,category=cat,cost=price*65//100,list_price=price,stock=0 if n%17==0 else 2 if n%11==0 else 24+n%15))
    with (dest/'store.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (dest/'policy.json').write_text(json.dumps(policy,indent=2))
    (dest/'dev.jsonl').write_text('\n'.join(json.dumps({'source':'SIMULATED','persona':p,'seed':s}) for s,p in enumerate(['fair','lowballer','bluffer']*10))+'\n')
    (ROOT/'starter').mkdir(exist_ok=True)
    (ROOT/'starter'/'.gitkeep').touch()
if __name__=='__main__': main()

