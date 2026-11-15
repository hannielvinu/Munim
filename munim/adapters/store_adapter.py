import csv, json, os
from pathlib import Path
from munim.models import Item
ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ('store.csv', 'policy.json', 'harness.py', 'evaluate.py')

def kit_path():
    requested = os.getenv('MUNIM_KIT', 'auto')
    official = ROOT / 'starter'
    complete = all((official / name).is_file() for name in REQUIRED)
    if requested == 'official' and not complete:
        raise ValueError('Official kit incomplete: need ' + ', '.join(REQUIRED))
    return official if complete and requested != 'standin' else ROOT / 'standin_kit'

def load_catalogue():
    path = kit_path()
    with (path / 'store.csv').open(encoding='utf-8-sig', newline='') as f:
        items = [Item(**{k: int(v) if k in ('cost','list_price','stock') else v for k,v in row.items()}) for row in csv.DictReader(f)]
    policy = json.loads((path / 'policy.json').read_text())
    if policy.get('margin_basis') != 'cost' or policy.get('discount_basis') != 'list_price':
        raise ValueError('Unsupported policy definition: update adapter, never guess official semantics')
    if len({i.id for i in items}) != len(items): raise ValueError('Duplicate IDs')
    for i in items:
        p=policy['categories'][i.category]
        if not 0 <= p['max_discount_bps'] < 10000 or p['min_margin_bps'] < 0: raise ValueError('Invalid policy')
    return {i.id:i for i in items}, policy, 'OFFICIAL' if path.name == 'starter' else 'SIMULATED'

