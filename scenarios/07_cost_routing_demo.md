# Scenario 07 — Tiered Model Routing with Cost Ledger

## Business pain point
Enterprise AI programs care about unit economics. Running every query through
the most capable (and most expensive) model is how pilots die at scale. A
routing layer that sends easy queries to fast/cheap models and escalates
only when needed can cut per-query cost by 3–10× with negligible quality
loss — if the routing decision itself is reliable.

## What to build
A three-tier router:

1. **Classifier (fast/cheap).** A small model or lightweight heuristic that
   labels an incoming question as `trivial | moderate | complex`.
2. **Dispatcher.** Routes `trivial` → a small/fast model (e.g., Haiku or
   Gemini Flash), `moderate` → a mid-tier model, `complex` → a frontier
   model (Sonnet, GPT-4-class, Gemini Pro).
3. **Cost ledger.** Every call appends a row: timestamp, route, tokens in,
   tokens out, cost estimate.

Use any scenario's corpus (compliance QA in scenario 05 is a natural fit) to
drive the router.

## Success criteria
- Router decision takes under 300ms.
- Ledger can answer: total cost this session, cost per route, average
  escalation rate.
- Manually crafted "obviously complex" questions route to the top tier;
  single-fact lookups route to the bottom tier.

## Tradeoffs to discuss
- **Classifier quality vs. speed.** A tiny model is fast but misclassifies;
  too much accuracy pushes latency into the bottom-tier model's budget.
- **Escalation on low confidence.** When the bottom-tier model says "I'm
  not sure," do you re-run on a higher tier or refuse? Depends on the
  cost of a wrong answer vs. the cost of a refusal.
- **Budget guardrails.** Per-user or per-session caps prevent runaway
  spend; they also surprise users when they hit. Soft-limit warnings
  before hard limits are the usual ergonomic fix.

## What I'd do with more time
_Fill this in after building._
