# Munim — the digital khata
**SIMULATED shop · OFFLINE scripted buyers · MOCK Rezolve.**

Cheap talk is free, commitments are priced. Munim separates buyer pressure from price-changing commitments, checks every outward offer against policy, and exposes the evidence in a warm shopkeeper workspace.

## Five-command quickstart
Python 3.11 and Node 22+ required. Windows: replace python with py -3.11 until the virtual environment is active.
1. `python -m venv .venv`
2. Activate: `source .venv/bin/activate` (PowerShell: `.venv\\Scripts\\Activate.ps1`)
3. `pip install -r requirements.txt`
4. `npm --prefix web ci && npm --prefix web run build` (run separately in Windows PowerShell 5)
5. `python -m uvicorn api.main:app --host 127.0.0.1 --port 8000`

Open http://127.0.0.1:8000. Saved simulated outputs are included. Never expose this unauthenticated, local shopkeeper demo publicly: it intentionally shows private diagnostics.

## Reproduce
- `python -m arena.run --n 200 --seed 7`: both brains, 400 negotiations.
- `python -m arena.tune`: training sweep, frozen config, held-out arena, replays and simulated development evaluation.
- `python -m pytest -q`: gate property tests and adversarial replay.
- `python scripts/e2e.py`: running UI checks and responsive screenshots; install browser via `python -m playwright install chromium`.
- `bash scripts/make_video.sh`: neural narrated UI recording; running local server required.
- `python submission/check.py`: package validation.
- `bash scripts/package_submission.sh`: ready-to-upload folder archive.

The evaluated default is selected by saved score in config.yaml. The live demo starts with the commitment ladder to illustrate the core idea. Baseline pricing is explicitly deadline-based. Both brains ignore pressure but only the ladder restricts concessions to new commitments.

## Layout
munim/ core + format adapters; standin_kit/ synthetic catalogue and evaluator; arena/ buyer personas, independent checker and replay; api/ FastAPI; web/ React; outputs/ evidence; submission/ portal artifacts; scripts/ reproducible tooling.

## Rezolve capabilities
munim/rezolve.py Rezolve.lookup: mock indexed retrieval with documented live adapter hooks.
munim/rezolve.py Rezolve.verify: mock price/stock verification against tool trace, fail closed.
munim/adapters/rezolve_adapter.py LiveClient.call: configurable HTTP paths/shapes, timeout, retry, request credits. No real provider endpoints were guessed.

See docs/ASSUMPTIONS.md, docs/TUNING.md, docs/REZOLVE_INTEGRATION.md and docs/SWAP_IN_REAL_KIT.md. Mandatory live provider use, official development evaluation and the approved abstract still require human inputs. This is a complete offline demonstration, not an official submission certification.

