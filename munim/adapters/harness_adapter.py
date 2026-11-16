from munim.agent import Agent
class Seller:
    def __init__(self,**kwargs): self.agent=Agent(**kwargs)
    def respond(self,message):
        result=self.agent.respond(message)
        # Harness consumers are buyers, not the private shopkeeper inspector.
        return {k:v for k,v in result.items() if k in ('source','round','move','text','closed','blocked','error')}
def seller(message,state=None):
    instance=state if isinstance(state,Seller) else Seller()
    return instance.respond(message),instance

