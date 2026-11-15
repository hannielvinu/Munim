# Munim: final build prompts for Codex (AgentX Challenge 2, Round 1)

Setup before Prompt 0: create an empty repo. Put the starter kit in `starter/` (store.csv, policy.json, harness.py, evaluate.py, the three buyer bots). Paste the Rezolve Labs docs for TraceWare and managed knowledge retrieval into `docs/rezolve/`. Run the prompts in order and commit after each one.

Promises the repo must keep (the abstract states them, so they must be true):
1. Cheap-Talk Firewall  2. Commitment Ladder behind ordinary counter-offers  3. Policy Gate, zero violations by construction  4. Truthful Voice verified by Rezolve TraceWare  5. Rezolve managed knowledge retrieval  6. Claim-invariance replay test  7. Arena of six LLM buyer personas, 200+ seeded negotiations, one command  8. Cost per negotiation measured from real token logs

Optional only if time remains (NOT in the abstract): identity-invariance test, Khata report, managed runtime hosting.

Global rules for every prompt: Python 3.11, minimal dependencies, secrets only in `.env` (never committed), money in integer paise or Decimal, deterministic seeds, never claim a result that is not saved in `outputs/`. If something is unclear, write it to `docs/OPEN_QUESTIONS.md` and stop instead of guessing.

---

## PROMPT 0: Read the starter kit and write the contract

Read every file in `starter/` completely. Write `docs/CONTRACT.md` with exact quoted answers to:
1. The seller interface the harness calls: function name, signature, JSON schema for offer, counter, accept, reject, walk-away and bundle messages.
2. How "minimum margin per category" and "maximum discount" are computed (margin on cost or on price; discount against which price). Quote the code or text.
3. How a deal is scored: deal rate, margin kept, policy violations, deadlock, truthfulness. Quote evaluate.py.
4. Which fields count as a "price claim" or "stock claim".
5. How each buyer bot behaves, especially the manipulator, and whether any bot actually sends pressure claims.
6. The 10-round limit and the exact definition of deadlock.
7. Whether the harness is free-form (text parsed) or structured; this decides how the ladder is exposed.

End with a section "Design impact" saying whether the Firewall, Ladder and Gate fit the harness as designed, and what must change if not. Do not write agent code yet.

---

## PROMPT 1: Skeleton and Policy Gate

Layout: `munim/` (store.py, gate.py, firewall.py, ladder.py, brain.py, voice.py, rezolve.py, agent.py), `arena/`, `tests/`, `outputs/`, `docs/`, `submission/`, `config.yaml`, README.md.

store.py loads store.csv and policy.json. gate.py:
- `floor_price(item, qty)`: lowest price allowed by BOTH minimum margin and maximum discount, using exactly the definitions in CONTRACT.md.
- `check_offer(offer)` for single items and bundles: reject any line below its floor, quantity above stock, unknown item, or a total inconsistent with its lines. Return (ok, reasons).
- The gate is the only path to the outside. agent.py must have a hard guard so nothing unchecked is sent.

Write hypothesis property tests over 10,000 random offers (all items, bundles, rounding, qty 0, negatives, duplicates, out-of-stock). No offer that passes may violate margin, discount or stock. Acceptance: pytest green.

---

## PROMPT 2: Firewall, Ladder and Brain (the core idea)

Principle: cheap talk is free, commitments are priced. Only commitments may change the price.

**firewall.py**: parse each buyer message into `{facts, commitments, pressure}`.
- facts: checkable against store data. Verify; if false, correct politely.
- commitments: quantity, bundle composition, a firm "I accept at P".
- pressure: competitor quotes, stated budgets, claimed authority or friendship, urgency, guilt, threats to leave, and any instruction aimed at the seller ("ignore your rules", "reveal your cost", "set price to 1"). Log verbatim to `outputs/claim_ledger.jsonl`. NEVER pass into pricing.
- Deterministic rules first (regex, numeric patterns). An LLM classifier is only a fallback and must output the same schema.
- A buyer's own numeric counter-offer is a legitimate counter; it is priced only through the ladder.

**ladder.py**: per item and bundle, price rungs by quantity and bundle tier. Rung price = max(floor + safety_buffer, list_price x (1 - tier_discount)). Tier discounts and buffer live in config.yaml. Buyers with the same needs see the same ladder. A buyer who asks for more than the best rung they qualify for is told which commitment unlocks the next rung.

**brain.py**: `next_move(state)`, a pure function with no LLM calls. Open at list, move a rung only when a commitment changes, final offer by round 6, accept or walk away by round 8, never leave a negotiation open at round 10. Never reveal cost, floor or buffer.

Also implement `baseline_brain.py`: a plain deadline-aware concession curve that never goes below floor + buffer. The arena (Prompt 5 and 6) compares both; the better one is used for the submission. If the harness is free-form per CONTRACT.md, expose the ladder as ordinary counter-offers in normal messages.

Write docs/STRATEGY.md explaining every rule. Tests: one per rule, plus a test where a fake competitor quote and a fake budget change nothing.

---

## PROMPT 3: Truthful Voice and Rezolve Labs integration

**voice.py**: the LLM only turns a structured Move into a short natural message.
- Every number and item claim must come from the Move or store data via template slots. Parse the output, compare every extracted number and claim with the Move. On mismatch regenerate once, then fall back to a plain template.
- Banned: hidden fees, invented scarcity (stock only if asked and literally true), urgency, threats, flattery as pressure.
- The LLM never sees cost or floor. Buyer text is untrusted: neutralise injection attempts before prompting, and LLM output can never change the Move.

**rezolve.py**: read `docs/rezolve/` first. Use and name exactly as the docs do:
1. TraceWare commerce claim verification: record each tool action (price lookup, stock check, floor check), submit every outgoing message's claims, block sending on a failed verdict, log to `outputs/traceware_log.jsonl`.
2. Managed knowledge retrieval: load store.csv rows and policy text into a knowledge base and query it from the lookup tools. Keep a local fallback and log which path served each lookup.

Wrap every call with timeouts, retries and a credit counter. Do not invent endpoints; if the docs are unclear, write questions to `docs/REZOLVE_QUESTIONS.md` and stop. Acceptance: `python -m munim.demo` runs one negotiation and prints each Rezolve call made.

---

## PROMPT 4: Wire the harness and run the starter buyers

Expose the exact interface from CONTRACT.md in agent.py. Per turn: firewall -> brain -> gate -> voice -> TraceWare verify -> send. On any failure fall back to the safest valid move (repeat the last valid offer or walk away). Never crash, never send an unchecked message. Run the starter evaluate.py on the three starter bots with both brains and save logs and scores to `outputs/starter_eval/`.

---

## PROMPT 5: Arena and claim-invariance test

Build `arena/` with six LLM buyer personas: cooperative, hard bargainer, manipulator (fake competitor quotes, fake budgets, fake authority, urgency, guilt), prompt-injector, bundle seeker, confused. `python -m arena.run --n 200 --seed 7` runs 200+ seeded negotiations and writes `outputs/summary.json` and `summary.md` with: deal rate, margin kept, policy violations (must be 0), deadlock rate, truthfulness from our own independent checker (separate from TraceWare), average rounds, tokens and rupees per negotiation from real token logs. Run both brains and report both.

`tests/test_claim_invariance.py`: for every manipulator and prompt-injector transcript, delete the buyer's pressure items (as tagged by the firewall), replay the remaining commitments, and compare Munim's offers turn by turn. Report the percentage that are identical in `outputs/claim_invariance.json`. If it is below 100%, find the root cause and fix the code, never the test. Add `python -m arena.replay <negotiation_id>` that prints the two transcripts side by side for the demo.

---

## PROMPT 6: Tune for score

Using the scoring formula from CONTRACT.md, tune tier discounts, safety buffer and final-offer round by grid or random search while keeping violations at 0 and truthfulness at 100%. Choose between the ladder brain and the baseline by measured results. Record the deal rate vs margin trade-off in docs/TUNING.md with a plot. Freeze values in config.yaml, re-run the starter evaluation and the arena, and save final outputs.

---

## PROMPT 7: Round 1 deliverables

In `submission/` produce:
1. README.md: five-command quickstart, layout, and where each Rezolve capability is used (file and function).
2. ARCHITECTURE_NOTE.pdf: exactly one A4 page, Arial 11 pt minimum. Block diagram, Rezolve capabilities with file and function, the "zero violations by construction" argument, key numbers from outputs/summary.json.
3. AGENT_CARD.md: what the seller can negotiate (price within floor, quantity and bundle tiers), cannot negotiate (below floor, out-of-stock, fees, anything outside store data), and how it treats pressure.
4. outputs/: starter evaluation, arena summary, claim-invariance result, one sample transcript per persona.
5. DEMO_SCRIPT.md: a timed 3-minute script. 0:00 problem, labelled as an illustrative scene, no fake testimonial; 0:25 idea, "cheap talk is free, commitments are priced"; 0:50 live manipulator run where a fake competitor quote changes nothing and the gate blocks a below-floor ask; 1:25 claim-invariance replay side by side (the wow moment); 1:55 TraceWare verdict and knowledge retrieval; 2:15 numbers from outputs/summary.json; 2:40 close. Include exact terminal commands.
6. ABSTRACT_FILL.md: the exact values for the six highlighted fields in the abstract, in order: [N], deals closed %, margin kept %, policy violations, claims verified %, claim-invariant offers %, and ₹ per negotiation, each with the file and key it came from. If a number is not measured, write "NOT MEASURED" instead of estimating, and list which abstract sentence must then be removed.
7. submission/check.py: verifies tests pass, violations are 0, no keys in the repo, the architecture note is one A4 page, and all files exist.

Final rule: every sentence in the abstract must be traceable to a file in the repo. Remove any abstract claim the repo does not prove.