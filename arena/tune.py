import json,itertools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yaml
from munim.logging import ROOT
from munim.ladder import settings
from arena.run import run,run_dev
from arena.replay import run_replays
def main():
    trials=[]; base=settings()
    for discount,buffer,final in itertools.product([300,500],[0,25],[5,6]):
        c={**base,'quantity_tiers':{1:0,3:discount,6:discount*2},'safety_buffer_paise':buffer,'final_offer_round':final}
        summary,_=run(24,1007,ROOT/'outputs/tuning_scratch',c)
        for b,m in summary['brains'].items():
            trials.append({'config':{**c,'brain':b},'metrics':m})
    valid=[t for t in trials if t['metrics']['policy_violations']==0 and t['metrics']['truthfulness']==1]
    best=max(valid,key=lambda t:t['metrics']['score'])
    (ROOT/'config.yaml').write_text(yaml.safe_dump(best['config'],sort_keys=False))
    (ROOT/'outputs/SIMULATED_tuning.json').write_text(json.dumps(trials,indent=2))
    fig,ax=plt.subplots(figsize=(7,4))
    for b,color in [('ladder','#2F3E9E'),('baseline','#E8891D')]:
        ts=[t for t in trials if t['config']['brain']==b]
        ax.scatter([t['metrics']['deal_rate']*100 for t in ts],[t['metrics']['margin_kept']*100 for t in ts],label=b,color=color,s=70)
    ax.set(xlabel='Deals closed (%)',ylabel='List gross margin kept (%)',title='SIMULATED tuning: 24 training cases per candidate')
    ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'outputs/SIMULATED_tuning.png'); plt.close(fig)
    (ROOT/'docs/TUNING.md').write_text('# SIMULATED tuning\n\nEight configurations, both brains, 24 training cases per brain, seed 1007. Final evaluation uses 200 cases per brain, seed 7, disjoint seeds. This is synthetic validation, not generalisation evidence. Select maximum saved score subject to zero violations and full independent truthfulness. Ties follow stable candidate order.\n\nSelected: '+json.dumps(best['config'])+'\n\n![Measured trade-off](../outputs/SIMULATED_tuning.png)\n\nAll trials: outputs/SIMULATED_tuning.json. Final results: outputs/summary.json. Baseline concessions are explicitly time-based; the ladder-only promise applies only to the ladder strategy.')
    summary,records=run(200,7); invariance=run_replays(records); run_dev()
    print(json.dumps({'summary':summary,'invariance_pct':invariance['identical_pct']},indent=2))
if __name__=='__main__': main()

