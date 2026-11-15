# Enable live Rezolve
Follow the five-step checklist in ../docs/REZOLVE_INTEGRATION.md. Configure all TODO fields in config/rezolve.yaml from official documentation. Add secrets only to .env, set REZOLVE_MODE=live and run python -m munim.demo. A key alone is insufficient: documented paths, payloads and verdict mapping must be configured. Failed verification blocks delivery. Re-run the arena and regenerate artifacts; never relabel old MOCK evidence.

