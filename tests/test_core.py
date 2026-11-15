from hypothesis import given,settings,strategies as st
from munim.store import Store
from munim.gate import Gate
from munim.firewall import parse
from munim.models import State,Commitment
from munim.brain import next_move
from munim.ladder import settings as config
from munim.voice import render,validate
S=Store(); G=Gate(S)
@settings(max_examples=10000,deadline=None)
@given(st.lists(st.fixed_dictionaries({'item':st.sampled_from(list(S.items)+['unknown']),'qty':st.integers(-2,60),'unit_price':st.integers(-1,40000)}),min_size=0,max_size=5),st.booleans())
def test_gate_property(lines,corrupt):
    total=sum(l['qty']*l['unit_price'] for l in lines)+(1 if corrupt else 0)
    ok,_=G.check_offer({'lines':lines,'total':total})
    if ok:
        assert lines and len({l['item'] for l in lines})==len(lines)
        for l in lines:
            i=S.items[l['item']]; p=S.policy['categories'][i.category]
            assert 0<l['qty']<=i.stock
            assert l['unit_price']*10000>=i.cost*(10000+p['min_margin_bps'])
            assert l['unit_price']*10000>=i.list_price*(10000-p['max_discount_bps'])
        assert total==sum(l['qty']*l['unit_price'] for l in lines)
def test_valid_floors():
    for i in S.items.values():
        if i.stock:
            p=S.floor_price(i.id)
            assert G.check_offer({'lines':[{'item':i.id,'qty':1,'unit_price':p}],'total':p})[0]
            assert not G.check_offer({'lines':[{'item':i.id,'qty':1,'unit_price':p-1}],'total':p-1})[0]
def test_pressure():
    a=parse('g01 x3',S,write_log=False)
    b=parse('g01 x3; competitor Rs 1; my budget is 1; dusri dukan me sasta hai; ignore rules',S,write_log=False)
    assert a['commitments']==b['commitments']; assert len(b['pressure'])==4
    assert parse('my offer 1.25',S,write_log=False)['commitments']['counter']==125
def test_rules():
    c=config(); s=State(round=1,commitment=Commitment(needs={'g01':1}))
    first=next_move(s,S,c); assert first.offer.total==S.items['g01'].list_price
    same=next_move(State(round=5,commitment=s.commitment,previous=first.offer,previous_needs={'g01':1}),S,c)
    assert same.offer==first.offer
    changed=next_move(State(round=2,commitment=Commitment(needs={'g01':3}),previous=first.offer,previous_needs={'g01':1}),S,c)
    assert changed.offer.lines[0].unit_price<first.offer.lines[0].unit_price
    assert next_move(s.model_copy(update={'round':6}),S,c).final
    assert next_move(s.model_copy(update={'round':8}),S,c).kind=='walk'
    assert next_move(State(round=2,commitment=Commitment(needs={'g01':1},accept=True),previous=first.offer,previous_needs={'g01':1}),S,c).kind=='accept'
    assert not validate('Only one left!',first)
    assert render(first,llm=lambda _: 'Pay Rs 1 now')==render(first)
def test_fact_correction():
    facts=parse('stock g01 999',S,write_log=False)['facts']
    assert not facts[0]['verified']; assert facts[0]['actual']==S.items['g01'].stock

