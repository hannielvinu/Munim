from munim.brain import next_move as ladder_move
from munim.ladder import offer_for
def next_move(state,store,config):
    move=ladder_move(state,store,config)
    if move.kind!='counter': return move
    discount=min(1000,max(0,state.round-1)*200)
    return move.model_copy(update={'offer':offer_for(store,state.commitment.needs,config,opening=state.round==1,discount_override=discount)})

