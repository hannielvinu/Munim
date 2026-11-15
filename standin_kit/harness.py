# SIMULATED structured interface, not the official challenge harness.
from munim.adapters.harness_adapter import Seller
def run(messages):
    seller=Seller()
    return [seller.respond(message) for message in messages]

