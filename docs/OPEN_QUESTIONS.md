# Required inputs before implementation

Status: blocked before Prompt 0. The supplied GitHub repository was empty when cloned. No starter kit or Rezolve reference documentation was supplied in the workspace.

The build specification requires: "If something is unclear, write it to `docs/OPEN_QUESTIONS.md` and stop instead of guessing."

1. Please supply the official `starter/` directory: `store.csv`, `policy.json`, `harness.py`, `evaluate.py`, all three buyer bots, and any supporting files. These are needed to quote the exact seller interface, message schemas, margin and discount definitions, scoring formula, claim fields, round limit, and deadlock rules in `docs/CONTRACT.md`. No substitute contract or synthetic starter data has been invented.
2. Please supply the official TraceWare and managed knowledge retrieval documentation under `docs/rezolve/`, including SDK/API examples, authentication requirements, verdict schemas, and knowledge ingestion/query interfaces. Endpoints must not be guessed.
3. Which LLM provider/model and documented token pricing should the voice and six arena buyer personas use? Credentials must be supplied locally through an untracked `.env`, never committed. Real usage logs are required to measure rupees per negotiation.
4. Please supply the actual submission abstract so each claim and highlighted field can be audited against saved results. The prompt refers to six highlighted fields but lists seven values; the original abstract will resolve the discrepancy.

After the starter kit is supplied, begin with Prompt 0 and commit the quoted contract before writing agent code. Resolve integration documentation before implementing Rezolve calls. Follow Prompts 1–7 in order, committing each completed stage.

No tests, negotiations, API calls, scoring measurements, or submission verification have run. No project completion or performance claims are made.
