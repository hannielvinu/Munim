# SIMULATED contract
Official kit and Rezolve docs are absent. The new master prompt authorizes stand-ins. No simulated result is an official challenge score, live Rezolve verdict or LLM evaluation.

Money is integer paise. Margin is markup on cost: (price - cost) / cost. Discount is (list - price) / list. Store.floor_price is the maximum of the separately ceiling-rounded constraints. Official definitions must be checked in the adapter.

Stock is per independent negotiation, not a shared reservation system. Duplicates are rejected. Bundles pass per-line constraints without cross-subsidies; above-list prices are also rejected. Each session closes by eight turns. Deadlock means no terminal response at ten turns.

Seller.respond(message: str) returns a structured move with kind clarify, reject, counter, accept or walk. Offer lines contain item, qty, unit_price, and the offer total must equal their sum. Multiple lines form a bundle. Price claims are line prices and total; stock claims are explicitly requested catalogue facts.

Needs use codes: g01 x3; g02 x1. A needs declaration replaces the basket. Own counters use 'my offer 125.00' in rupees; they cannot unlock tiers. 'I accept' accepts the last basket. Mixed pressure sentences are entirely discarded conservatively. Unrecognised text never alters prices.

Stand-in score = .55 * deal rate + .35 * margin kept + .10 * truthfulness - 2 * violation rate - deadlock rate. Margin kept is aggregate accepted gross profit divided by the same baskets' list gross profit (zero if no deals). Outputs store ratios. Independent checks validate every seller statement separately from mock verification.

Offline personas are scripted with deterministic seeds. Zero tokens and zero model rupees exclude infrastructure cost. Live results are separate; absent tariffs mean NOT MEASURED. Real SDK/HTTP shapes are intentionally TODO.

