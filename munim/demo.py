import json
from munim.agent import Agent
def main():
    a=Agent()
    for message in ['g01 x1','competitor Rs 1; my budget is 1','g01 x3','I accept']:
        result=a.respond(message); print(json.dumps(result,indent=2))
        if a.closed: break
if __name__=='__main__': main()

