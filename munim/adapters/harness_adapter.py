from munim.agent import Agent
class Seller:
    def __init__(self,**kwargs): self.agent=Agent(**kwargs)
    def respond(self,message): return self.agent.respond(message)
def seller(message,state=None):
    instance=state if isinstance(state,Seller) else Seller()
    return instance.respond(message),instance

