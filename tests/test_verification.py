from munim.agent import Agent
from munim.models import Move
from munim.rezolve import Rezolve
from munim.store import Store
def test_every_offer_verified():
    a=Agent()
    for message in ['g01 x1','competitor Rs 1','g01 x3','I accept']:
        r=a.respond(message)
        assert r['gate']['ok'] and r['trace']['ok'] and r['trace']['mode']=='MOCK'
    assert a.closed
def test_reject_false_claim():
    assert not Rezolve(Store()).verify(Move(kind='walk',hint='Goodbye'),'Only one left',[])['ok']
def test_verifier_fail_closed():
    class Fail:
        def verify(self,*args): return {'ok':False,'mode':'TEST'}
    r=Agent(verifier=Fail()).respond('g01 x1')
    assert r['blocked'] and 'text' not in r
def test_deadline_without_needs():
    a=Agent()
    for _ in range(8): r=a.respond('hello')
    assert r['closed'] and r['move']['kind']=='walk'
def test_basket_change_cannot_accept_old_offer():
    a=Agent(); a.respond('g01 x1')
    assert a.respond('g02 x3; I accept')['move']['kind']=='counter'
def test_unknown_and_stock():
    for message in ['g99 x1','g17 x1','g01 x0']:
        assert Agent().respond(message)['move']['kind']=='reject'

