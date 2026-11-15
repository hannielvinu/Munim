from munim.models import Move
from munim.ladder import offer_for,next_hint
def next_move(state,store,config):
    c=state.commitment
    if state.round>=config['walk_round']:
        if c.accept and state.previous is not None and c.needs==state.previous_needs: return Move(kind='accept',offer=state.previous)
        return Move(kind='walk',hint='No agreement reached. Thank you for visiting.')
    if not c.needs: return Move(kind='clarify',hint='Choose an item and quantity using its catalogue code.')
    if any(k not in store.items or q<=0 or q>store.items[k].stock for k,q in c.needs.items()):
        return Move(kind='reject',hint='That quantity or item is unavailable. Please choose from the catalogue.')
    if c.accept and state.previous is not None and c.needs==state.previous_needs: return Move(kind='accept',offer=state.previous)
    if state.round==1: offer=offer_for(store,c.needs,config,opening=True)
    elif c.needs==state.previous_needs and state.previous is not None: offer=state.previous
    else: offer=offer_for(store,c.needs,config)
    return Move(kind='counter',offer=offer,final=state.round>=config['final_offer_round'],hint=next_hint(c.needs))

