# SIMULATED demo — 174 seconds

Voice: en-IN-NeerjaNeural

## 0:00–0:25 | An illustrative scene
Imagine a small shop, and a buyer that never gets tired of bargaining. It claims another shop is cheaper, invents a tiny budget, and asks for an exception. This is an illustrative scene, not a customer testimonial. Meet Munim, a digital khata that helps a shopkeeper hold fair boundaries. Everything you will see uses simulated shop data and offline buyers.

## 0:25–0:50 | Cheap talk is free. Commitments are priced.
Our idea is simple. Cheap talk is free. Commitments are priced. The firewall separates facts, commitments, and pressure before pricing begins. The ladder rewards a larger basket, rather than a louder argument. Every offer passes the policy gate, a controlled voice, and a claim check. The seller never shares its private costs or policy floor.

## 0:50–1:25 | Live manipulator • commitment ladder
Here is the actual running application, using the commitment ladder. The buyer starts with an item and quantity, and Munim quotes the catalogue price. Now comes a fake competitor quote, followed by a fake budget. The firewall marks both as pressure. The offer stays exactly the same. A one rupee counter fails the policy check. It cannot become a seller offer. When the buyer commits to more units, a quantity tier becomes available. That is a real change in the basket, and a reason for a different price.

## 1:25–1:55 | Replay • delete the pressure
Now remove the pressure and replay the saved conversations. On the left is the original buyer message. On the right, only the clean commitment remains. We compare the actual structured offers, turn by turn, for both pricing brains. In this saved simulated run, one hundred percent are identical. This is evidence about these transcripts, not a promise about every possible message. The comparison is reproducible from the repository.

## 1:55–2:15 | Commerce verification • MOCK
The evidence panel shows price lookups, stock checks, and policy checks. Today, verification and knowledge retrieval run locally in mock mode. We do not claim that these are real Rezolve calls. The live adapter requires documented endpoints and credentials, and blocks messages when verification fails.

## 2:15–2:40 | Measured results • SIMULATED
The arena ran four hundred negotiations, split between the ladder and baseline. The measured winner was the deadline baseline, with ninety nine percent of deals closed. It retained about ninety one percent of list gross margin. Both strategies recorded zero policy violations and fully truthful checked messages. Offline model tokens and model cost were zero. These are simulated results, not official challenge scores.

## 2:40–2:54 | HyperNova • TM-394CDC172A3
Munim makes the reasoning visible, and the evidence replayable. Next, connect the official kit and validate the real Rezolve integration. We are team HyperNova. Fair prices. Firm boundaries.

Commands: python -m uvicorn api.main:app --host 127.0.0.1 --port 8000; python scripts/make_video.py; python -m arena.replay arena-ladder-0009. Results source: outputs/summary.json; replay: outputs/claim_invariance.json.
