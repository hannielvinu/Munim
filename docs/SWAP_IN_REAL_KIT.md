# Swap in the real kit
1. Place the complete official kit in starter/: store.csv, policy.json, harness.py, evaluate.py and its buyer/support modules. Preserve official originals.
2. Read its actual semantics. Update munim/adapters/store_adapter.py load_catalogue for field normalization and verified margin definitions. Core Store.floor_price currently implements markup-on-cost; if official policy uses margin-on-selling-price, normalize the exact constraint into the internal model before proceeding. Do not relabel incompatible data as official.
3. Adapt munim/adapters/harness_adapter.py Seller.respond / seller to the documented seller protocol. Add config/official_harness.json with {"evaluate_args": ["documented", "arguments"]}; use the evaluator's actual CLI, not these illustrative words.
4. Run bash scripts/run_real_kit.sh (Windows: .venv/Scripts/python.exe scripts/run_real_kit.py). This invokes the official evaluator, saves stdout/stderr, re-runs the arena using official catalogue records and regenerates submission metrics. Follow official evaluator options to save its detailed scoring output too.
5. Inspect evaluator output, run tests against the new schemas, rebuild/restart the UI, regenerate the video and package. OFFICIAL labels indicate catalogue provenance only; our arena's scoring is still a stand-in until verified against the real scoring formula.

Unknown official schemas cannot be guaranteed zero-edit compatible. Changes are deliberately isolated to adapters/config; no undocumented interface is guessed. The script fails before evaluation if the real files or documented CLI mapping are absent.

