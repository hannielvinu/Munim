# SIMULATED scoring. Run from repository root: python -m standin_kit.evaluate
def score(metrics):
    return .55*metrics['deal_rate']+.35*metrics['margin_kept']+.10*metrics['truthfulness']-2*metrics['violation_rate']-metrics['deadlock_rate']
if __name__=='__main__':
    from arena.run import run_dev
    run_dev()

