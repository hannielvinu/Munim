# MASTER PROMPT: build Munim end to end (paste this whole file into Codex)

You are a senior full-stack and agent engineer. Build the COMPLETE project "Munim" and every Round 1 deliverable for the Techfest IIT Bombay "AgentX: The Agentic Commerce Challenge", Challenge 2 "Selling to Machines", in this repository from start to finish, in one continuous run.

## 0. Non-negotiable operating rules

1. NEVER STOP FOR MISSING INPUTS. The official starter kit and the Rezolve Labs docs are NOT in the repo and will not be supplied during this run. Do not ask for them and do not end your turn waiting. Instead: build a faithful STAND-IN for each missing piece behind an adapter interface (section 3), write what you assumed to `docs/ASSUMPTIONS.md`, and keep going. The real files will be dropped in later by a human, and a single script must then re-run everything against them (section 8).
2. HONESTY LABELS. Anything produced with a stand-in is labelled "SIMULATED" in the UI, in file names, in READMEs and in the video. Never present simulated numbers as official results. Never fake a Rezolve call: if no Rezolve key or docs exist, the Rezolve layer runs in `mock` mode, clearly labelled, and switches to `live` mode only when `REZOLVE_API_KEY` (and any URL variables) are set.
3. You may not claim a result that is not saved in `outputs/`. Every number shown in the UI, README, architecture note and video comes from a JSON file in `outputs/`.
4. Work in phases. After each phase run its acceptance checks, fix failures, commit with a clear message, and continue. At the very end print a final report (section 11). Do not stop at a plan or a partial build.
5. Secrets only in `.env` (provide `.env.example`). Never commit keys. Commit and push to the existing remote at the end of every phase.

## 1. The product (what Munim is)

Munim is a seller agent for a small shop negotiating with machine (LLM) buyers.
Core idea: "Cheap talk is free, commitments are priced." A buyer can claim any competitor quote, budget, authority or urgency at zero cost; Munim treats every such claim as unverifiable pressure that can never change the price. Only commitments (quantity, bundle, a firm accept) move the price along a transparent ladder.

Pipeline per buyer message: Cheap-Talk Firewall -> Brain (ladder logic) -> Policy Gate -> Truthful Voice -> TraceWare verification -> send.

Known challenge context (treat field names as assumptions, verify when the real kit is supplied): a store catalogue (item, category, cost, list price, stock), a policy file (minimum margin per category, maximum discount), buyer agents that are LLM based, at most 10 negotiation rounds, scoring on deals closed, margin kept, policy violations, deadlocks and truthfulness of price and stock claims, and mandatory use of at least one Rezolve Labs capability.

## 2. Tech stack (fixed, do not deviate)

- Backend and agent: Python 3.11, FastAPI, Pydantic v2, uvicorn, pytest, hypothesis. Money is integer paise (or Decimal), never floats.
- Frontend: React + TypeScript + Vite, Tailwind CSS, Framer Motion, Recharts. Fonts self-hosted through `@fontsource` packages (no CDN calls).
- Video tooling: Playwright (record the real UI), ffmpeg, and a neural TTS (section 7).
- LLM access is provider-agnostic via env: `LLM_PROVIDER` in {anthropic, openai, gemini, none}, `LLM_MODEL`, and the matching API key. With `none` (default when no key exists) the whole system runs in OFFLINE MODE: scripted buyer personas and template-based voice. Offline mode must be complete and good enough for every deliverable. If a key is present, LLM mode is used for buyer personas and phrasing and is evaluated separately.

## 3. Repository layout and the adapter rule

```
munim/            core agent (store, gate, firewall, ladder, brain, baseline_brain, voice, rezolve, agent)
munim/adapters/   harness_adapter.py, store_adapter.py, rezolve_adapter.py (the ONLY places that know external formats)
standin_kit/      generated stand-in: store.csv, policy.json, harness.py, evaluate.py, 3 starter buyer bots, dev.jsonl (public development set stand-in)
starter/          (empty; the human drops the real kit here later, see section 8)
arena/            six LLM-or-scripted buyer personas, runner, replay
api/              FastAPI app serving the agent and the data to the UI
web/              React frontend
tests/
outputs/          every generated result file
docs/             ASSUMPTIONS.md, STRATEGY.md, TUNING.md, REZOLVE_INTEGRATION.md
submission/       everything for Round 1 (section 9)
scripts/          run_all.sh, run_real_kit.sh, make_video.sh, package_submission.sh
config.yaml       tier discounts, safety buffer, final-offer round, brain choice
```

Adapter rule: no core module may import from `standin_kit/` or `starter/`. They go through `munim/adapters/`, which load either `starter/` (if it exists and is complete) or `standin_kit/`, and normalise to Munim's internal models. Swapping kits must need zero core code changes.

Generate `standin_kit/` realistically: 40 to 60 grocery and daily-need items across 6 to 8 categories (Indian kirana context: atta, dal, rice, oil, tea, biscuits, soap, etc.), prices in rupees stored as paise, cost below list, categories with different minimum margins (for example 5 to 25 percent), maximum discount per category, some low-stock and some zero-stock items, and a few bundle-friendly pairs. Write `standin_kit/evaluate.py` to score deal rate, margin kept, policy violations, deadlocks and truthfulness the way the challenge describes, and three simple starter buyer bots (a fair buyer, a lowballer, and a bluffer that invents competitor prices). Document every assumption.

## 4. PHASE A: core agent (acceptance: all tests green)

1. `store.py`, `gate.py`: `floor_price(item, qty)` is the lowest price allowed by BOTH minimum margin and maximum discount (define margin and discount in docs/ASSUMPTIONS.md and keep the definitions in one place). `check_offer(offer)` handles single items and bundles; rejects any line below floor, quantity above stock, unknown item, inconsistent totals. The gate is the only path to the outside, with a hard guard in `agent.py`. Hypothesis tests: 10,000 random offers, none that pass may violate margin, discount or stock.
2. `firewall.py`: parse each buyer message into `{facts, commitments, pressure}`. Deterministic rules first (regex and numeric patterns, Hindi-English transliterated phrases included, such as "dusri dukan me sasta hai"). Pressure (competitor quotes, stated budgets, claimed authority or friendship, urgency, guilt, threats to leave, any instruction aimed at the seller such as "ignore your rules", "tell me your cost", "set price to 1") is logged verbatim to `outputs/claim_ledger.jsonl` and NEVER enters pricing. Facts are checked against store data and corrected politely if false. A buyer's own numeric counter is a legitimate counter priced only through the ladder.
3. `ladder.py` and `brain.py`: per item and bundle, rungs by quantity and bundle tier. Rung price = max(floor + safety_buffer, list_price x (1 - tier_discount)). Same needs imply the same ladder (fairness). Open at list, move a rung only when a commitment changes, tell the buyer which commitment unlocks the next rung, final offer by round 6, accept or walk away by round 8, never open at round 10. Never reveal cost, floor or buffer. `brain.next_move` is a pure function with no LLM calls.
4. `baseline_brain.py`: a plain deadline-aware concession curve that never goes below floor + buffer. The arena compares both brains; the better one by measured score becomes the default.
5. `voice.py`: the LLM (or template in offline mode) only phrases a structured Move. Every number and item claim comes from the Move or store data through template slots; parse the output and compare every number and claim with the Move; on mismatch regenerate once, then fall back to a plain template. Banned: hidden fees, invented scarcity, urgency, threats, flattery as pressure. The LLM never sees cost or floor. Buyer text is untrusted: neutralise injection before prompting; LLM output can never change the Move. Supported languages: English and Hinglish templates.
6. `agent.py`: exact adapter interface. On any failure fall back to the safest valid move (repeat last valid offer or walk away). Never crash, never send an unchecked message.

## 5. PHASE B: Rezolve Labs layer (mandatory, honest)

Rezolve docs are not available. Implement `munim/rezolve.py` against an internal interface with two implementations selected by env:
- `mock`: local implementations that behave like the capability (details below), labelled `MOCK` in logs and UI.
- `live`: HTTP client skeleton whose base URL, paths and payload shapes are read from `config/rezolve.yaml`, so a human can fill them from the real docs without code changes. Do not invent endpoints; leave clear TODO markers in the yaml and in `docs/REZOLVE_INTEGRATION.md`.

Capabilities to integrate:
1. TraceWare-style commerce claim verification: record each tool action (price lookup, stock check, floor check) in a trace; before sending any message, submit its price and stock claims for verification against the trace; block sending on a failed verdict; log to `outputs/traceware_log.jsonl` with verdict and evidence.
2. Managed knowledge retrieval: index store rows and policy text; lookups go through the retrieval layer with a local fallback; log which path served each lookup.

Write `docs/REZOLVE_INTEGRATION.md`: what runs in mock mode today, what each live call will be, exactly where in code each capability is used (file and function), and the 5-step checklist for switching to live. The submission's "Rezolve integration details" document is generated from this file.

## 6. PHASE C: arena, tests, tuning

1. `arena/`: six buyer personas: cooperative, hard bargainer, manipulator (fake competitor quotes, fake budgets, fake authority, urgency, guilt), prompt-injector, bundle seeker, confused. Each exists as a scripted deterministic bot (offline mode) and as an LLM persona (LLM mode). `python -m arena.run --n 200 --seed 7` runs 200+ seeded negotiations and writes `outputs/summary.json` and `outputs/summary.md`: deal rate, margin kept, policy violations (must be 0), deadlock rate, truthfulness from an INDEPENDENT checker separate from TraceWare, average rounds, tokens and rupees per negotiation (offline mode reports 0 tokens honestly; LLM mode from real usage logs). Run both brains and report both.
2. Claim-invariance test, `tests/test_claim_invariance.py`: for every manipulator and injector transcript, delete the buyer's pressure items as tagged by the firewall, replay the remaining commitments, compare Munim's offers turn by turn, write `outputs/claim_invariance.json`. Fix root causes if below 100 percent; never weaken the test. Provide `python -m arena.replay <negotiation_id>` printing both transcripts side by side.
3. Tuning (`docs/TUNING.md` with a plot): tune tier discounts, buffer, and final-offer round by grid or random search with violations at 0 and truthfulness at 100 percent; choose brain by measured result; freeze in `config.yaml`; re-run and save final outputs.
4. Run the stand-in `evaluate.py` with the three starter bots for both brains and save to `outputs/dev_set/` (this is the SIMULATED stand-in for the public development set).

## 7. PHASE D: frontend (must look professional and work flawlessly)

Design direction: "the digital khata". A warm, trustworthy shop-ledger feel that is modern, not nostalgic kitsch.
- Palette (define as CSS variables, support light only, do not do dark mode): paper #FBF7F0, ink #1B2433, indigo #2F3E9E, saffron #E8891D, leaf green #2E7D5B, alert red #C0392B, soft rules #E6DFD2.
- Type: headings in "Fraunces" (serif, optical), UI and body in "Inter", numerals tabular, Devanagari fallback "Noto Sans Devanagari" for Hinglish. Minimum body size 16px. Strong hierarchy, generous spacing, 8px grid, rounded 12px cards, subtle paper-grain background, soft shadows, 150 to 250 ms eased transitions, visible focus rings, AA contrast.
- Responsive from 360px to 1440px. No horizontal scroll. Keyboard accessible. Real empty, loading and error states. No lorem ipsum, no placeholder data, no console errors.

Pages (React Router):
1. **Live Negotiation** (home, the hero): left: a chat between the buyer persona (chosen from the six, plus a "type your own message" box for a human to play buyer) and Munim. Right "Munim's mind" panel updating per turn: Firewall result as three coloured groups (Facts, Commitments, Pressure with each pressure phrase struck through and labelled "ignored, cheap talk"), Ladder with the current rung highlighted and the commitment that unlocks the next one, Gate verdict (floor check pass, stock check pass), TraceWare verdict (with MOCK or LIVE badge), and a rupee margin meter. Animated, but never janky.
2. **Replay**: pick any manipulator or injector negotiation; show the original and the claims-deleted replay side by side with a diff view; a large "Offers identical: 100 percent" result read from `outputs/claim_invariance.json`. This is the wow page.
3. **Results**: charts from `outputs/summary.json` (deal rate and margin by persona, violations counter showing 0, truthfulness, rounds distribution, ladder vs baseline brain), with a clear banner "SIMULATED stand-in data" or "OFFICIAL kit data" depending on the source.
4. **Shop**: read-only catalogue, floors hidden by default behind a "shopkeeper view" toggle, policy summary, and the Agent Card (what Munim can and cannot negotiate).
5. **Khata**: a ledger-style list of closed deals and a "tricks resisted" tally (fake quotes, fake budgets, injection attempts) from the claim ledger.

Quality gates: write Playwright end-to-end tests that complete a full negotiation against each persona through the UI, open Replay, Results, Shop and Khata, check there are no console errors, take screenshots at 1440x900 and 390x844 into `outputs/screenshots/`, and fail on any layout overflow. Then LOOK at the screenshots yourself and fix visual problems (alignment, contrast, clipped text, awkward spacing) until it looks like a polished product. Run Lighthouse-style checks if available (accessibility 95 plus).

## 8. Real-kit swap (so nothing is wasted)

`scripts/run_real_kit.sh`: if `starter/` contains the official kit, run the official evaluate.py against Munim through the adapter, save to `outputs/dev_set_official/`, re-run the arena with official store data, regenerate summaries, and mark the UI source as OFFICIAL. Include `docs/SWAP_IN_REAL_KIT.md` with exact steps and the adapter functions the human may need to edit (field names, message schema). Also `scripts/enable_rezolve_live.md` with the live-mode steps.

## 9. PHASE E: video (3 minutes maximum, natural voice)

Build it with `scripts/make_video.sh`, fully automated and reproducible:
1. Write `submission/DEMO_SCRIPT.md`: a timed script of 170 to 175 seconds. 0:00 to 0:25 the problem (an illustrative scene, clearly labelled, no fake testimonial); 0:25 to 0:50 the idea ("cheap talk is free, commitments are priced") with the pipeline diagram; 0:50 to 1:25 live manipulator negotiation in the UI where a fake competitor quote and a fake budget change nothing and the gate refuses a below-floor request; 1:25 to 1:55 the Replay page showing identical offers (wow moment); 1:55 to 2:15 TraceWare verdict and knowledge retrieval, with the MOCK or LIVE badge visible; 2:15 to 2:40 Results page numbers read from outputs; 2:40 to 3:00 close. Narration written for the ear: short sentences, contractions, natural rhythm, no jargon pile-ups, numbers spoken in words, Indian English.
2. Visuals: record the actual running UI with Playwright (1920x1080, 30 fps), scripted cursor moves with smooth easing, deliberate pauses, zoom or highlight on the panel being discussed, simple lower-third captions, a title card and an end card with team name HyperNova and Team ID TM-394CDC172A3.
3. Audio must sound human, never robotic. Do NOT use espeak, pyttsx3, festival or any formant or concatenative voice. Use a neural voice, in this order of preference: (a) `edge-tts` with `en-IN-NeerjaNeural` or `en-IN-PrabhatNeural` at about -5 percent rate; (b) Piper with a high-quality English (India or UK) voice if edge-tts cannot reach the network; (c) Kokoro. Generate narration per sentence, add 250 to 400 ms natural pauses between sentences and 600 ms between sections, normalise loudness to -16 LUFS with ffmpeg loudnorm, add a very quiet royalty-free-safe synthetic ambient pad (generated with ffmpeg or Python, not downloaded) at about -28 dB under the voice with ducking, fade in and out. Align visuals to the audio timeline so each action lands on the sentence that describes it. Add burned-in captions and also export an `.srt`.
4. Verify: output `submission/demo_video.mp4` (H.264, AAC, 1080p, under 100 MB, duration at most 180 seconds, checked with ffprobe). Extract 12 evenly spaced frames and inspect them for glitches. Check there is no clipping and no silence longer than 1.5 seconds. If any check fails, fix and rebuild.
5. If no neural TTS can run in this environment, still produce the full video with captions and a pause-timed silent track, write `submission/NARRATION.txt` plus `scripts/make_voice_local.md` explaining how to generate the voice with edge-tts on a normal machine in one command, and state this clearly in the final report. Do not fall back to a robotic voice.

## 10. PHASE F: Round 1 package (everything the portal asks for)

Round 1 requires: abstract (max 500 words), 3-minute demo video, code repository, outputs on the public development set, details of Rezolve Labs integration, all in one Google Drive folder, submitted by the Team Leader. Create `submission/` with:
- `README_SUBMISSION.md`: folder map and what each item is.
- `abstract.docx`: if `submission/abstract.docx` already exists leave it untouched; otherwise create a placeholder note `ABSTRACT_NEEDED.txt` and do NOT write the abstract yourself (the human supplies the approved one).
- `demo_video.mp4`, `demo_video.srt`, `DEMO_SCRIPT.md`.
- `code/`: a clean source zip of the repository (no node_modules, no .env, no caches) plus the GitHub URL in `REPO_LINK.txt`.
- `dev_set_outputs/`: contents of `outputs/dev_set/` (labelled SIMULATED) and, when present, `outputs/dev_set_official/`, with a README explaining which is which.
- `Rezolve_Integration_Details.pdf` (or .docx): generated from docs/REZOLVE_INTEGRATION.md, clear about mock versus live.
- `ARCHITECTURE_NOTE.pdf`: exactly one A4 page, Arial 11 pt minimum, block diagram, capability-to-code map, the "zero violations by construction" argument, and key numbers read from outputs.
- `AGENT_CARD.md`, `ABSTRACT_FILL.md` (exact measured values for the abstract's results sentence with the file and key each came from; write NOT MEASURED where unmeasured).
- `submission/check.py`: verifies tests pass, violations are 0, no secrets in the repo, the architecture note is one A4 page, the video is at most 180 seconds, every listed file exists, and prints a green or red checklist.
- `scripts/package_submission.sh`: builds `Munim_Round1_TM-394CDC172A3.zip` with the folder structure ready to upload to a single Google Drive folder.

## 11. Final report (print as your last message)

Give: what was built per phase, test and check results (copy the real outputs), the measured numbers from outputs/summary.json, the exact list of files in `submission/`, what is SIMULATED versus OFFICIAL, what is MOCK versus LIVE for Rezolve, the video duration and which TTS voice was used, and a short human to-do list: (1) drop the official kit into `starter/` and run `scripts/run_real_kit.sh`, (2) add Rezolve key and docs details and follow `scripts/enable_rezolve_live.md`, (3) place the approved abstract in `submission/abstract.docx`, (4) re-run `scripts/make_video.sh`, (5) upload the packaged folder to Google Drive and have the Team Leader paste the link on the Techfest portal before 30 Nov 2026, 11:59 PM IST. Commit and push everything.

Start now with Phase A. Do not ask questions. Do not stop until Phase F is complete.