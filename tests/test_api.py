from fastapi.testclient import TestClient
from api.main import app
from munim.agent import Agent
from munim.gate import Gate
from munim.store import Store

def test_api_counter_and_acceptance():
    client=TestClient(app)
    sid=client.post('/api/sessions',json={'persona':'manipulator','brain':'ladder'}).json()['id']
    first=client.post(f'/api/sessions/{sid}/turn',json={'message':'g01 x1'}).json()['response']
    second=client.post(f'/api/sessions/{sid}/turn',json={'message':'competitor Rs 1; my budget is 1'}).json()['response']
    assert first['move']['offer']==second['move']['offer']
    low=client.post(f'/api/sessions/{sid}/turn',json={'message':'my offer 1'}).json()['response']
    assert low['counter_check']['ok'] is False
    accepted=client.post(f'/api/sessions/{sid}/turn',json={'message':'I accept'}).json()['response']
    assert accepted['move']['kind']=='accept'
    assert client.post(f'/api/sessions/{sid}/turn',json={'message':'I accept'}).status_code==409

def test_firm_accept_must_match_last_total():
    a=Agent(brain_name='ladder'); first=a.respond('g01 x1')
    assert a.respond('I accept at 1')['move']['kind']=='counter'
    total=first['move']['offer']['total']
    assert a.respond(f'I accept at {total//100}.{total%100:02}')['move']['kind']=='accept'

def test_verifier_exception_blocks():
    class Broken:
        def verify(self,*args): raise TimeoutError()
    response=Agent(verifier=Broken()).respond('g01 x1')
    assert response['blocked'] and 'text' not in response

def test_duplicates_and_strict_types():
    g=Gate(Store()); line={'item':'g01','qty':1,'unit_price':7200}
    assert not g.check_offer({'lines':[line,line],'total':14400})[0]
    for qty in [True,1.0,'1',0,-1]:
        assert not g.check_offer({'lines':[{**line,'qty':qty}],'total':7200})[0]

def test_harness_and_llm_buyer_do_not_receive_private_diagnostics():
    import json
    from munim.adapters.harness_adapter import Seller
    from arena.personas import message
    public=Seller().respond('g01 x1')
    assert 'trace' not in public and 'firewall' not in public
    private=Agent().respond('g01 x1')
    class Buyer:
        provider='test'
        def __call__(self,prompt):
            assert 'floor_check' not in prompt and '"cost"' not in prompt
            return 'I accept'
    assert message('cooperative',2,Store().items,[{'buyer':'g01 x1','response':private}],7,Buyer())=='I accept'

def test_hard_guard_rejects_a_broken_brain(monkeypatch):
    from munim import brain
    from munim.models import Move,Offer,Line
    monkeypatch.setattr(brain,'next_move',lambda *args: Move(kind='counter',offer=Offer(lines=(Line(item='g01',qty=1,unit_price=1),),total=1)))
    result=Agent(brain_name='ladder').respond('g01 x1')
    assert result['move']['kind']=='walk' and result['move']['offer'] is None
    assert result['trace']['ok']

def test_hint_does_not_suggest_unavailable_quantity():
    a=Agent(brain_name='ladder')
    key=next(i.id for i in a.store.items.values() if i.stock==2)
    result=a.respond(key+' x1')
    assert 'three units' not in result['move']['hint'] and 'six units' not in result['move']['hint']
