import json
from munim.logging import ROOT
from arena.replay import replay
def test_every_adversarial_transcript():
    records=json.loads((ROOT/'outputs/SIMULATED_transcripts.json').read_text())
    adversarial=[r for r in records if r['persona'] in ('manipulator','prompt-injector')]
    assert adversarial
    for r in adversarial: assert replay(r)['identical'],r['id']

