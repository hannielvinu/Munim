# Rezolve integration details — MOCK, not live-certified
No official SDK documentation or credentials were available. All delivered verification/retrieval results are local MOCK simulations. Mandatory use of an actual Rezolve capability remains unverified.

## Capability-to-code map
munim/rezolve.py: Rezolve.lookup indexes catalogue rows and policy, queries managed retrieval in LIVE mode and logs local fallback on failure or inconsistent data. Rezolve.verify records price lookup, stock check and floor check evidence before checking each outward price/stock claim. Agent.respond blocks delivery if verification fails.

munim/adapters/rezolve_adapter.py: LiveClient.call is the sole HTTP boundary. Configurable paths, request templates, response paths, authentication header, timeout, retries and request credit limit live in config/rezolve.yaml. A credit is a counted request attempt, not a claim about provider billing. No provider endpoint or schema is invented.

Logs: outputs/traceware_log.jsonl, retrieval_log.jsonl and rezolve_calls.jsonl distinguish MOCK, LIVE and local_fallback. The mock policy index is local and rebuilt per session. A production managed index would be provisioned once; this reference skeleton ingests per session.

## Five steps to enable live
1. Read official provider docs and confirm both named capabilities are supported.
2. Fill every TODO in config/rezolve.yaml using documented paths, request templates and response paths. Map verify to a strict boolean verdict. Replace the illustrative payload keys with the documented schema.
3. Add REZOLVE_API_KEY and an HTTPS REZOLVE_BASE_URL to local .env. Never commit secrets.
4. Set REZOLVE_MODE=live, run python -m munim.demo, inspect actual request logs and test a deliberately false claim. Missing docs, credentials, timeout or a failed verdict must block delivery.
5. Re-run tests, arena, submission generation and video; report live results only when the saved evidence demonstrates actual successful provider calls.

This layer is a configurable integration scaffold. It does not prove compatibility with an undocumented external API, nor satisfy mandatory provider usage until a human configures and validates the real service.

