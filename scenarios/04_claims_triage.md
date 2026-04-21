# Scenario 04 — Multi-Agent Claims Triage

## Business pain point
Insurance claims take a median of 14 days to process end-to-end. Much of that
is handoff friction: intake → adjuster → SIU (fraud) → payment. An agentic
system that pre-processes each claim — retrieving context, flagging fraud
indicators, and drafting an adjuster summary — can compress the cycle
meaningfully.

## What to build
A three-agent pipeline:

1. **Retrieval agent.** Given a claim ID, pulls the claim record,
   narrative(s), and any existing fraud indicators via `GET /claims/{id}`.
2. **Fraud classifier agent.** Scores fraud risk on a 0–1 scale using both
   the structured indicators and narrative text. Must explain its score.
3. **Summary agent.** Produces an adjuster-ready brief: timeline, anomalies,
   recommended next step (approve / request docs / refer SIU).

Agents should pass structured state between each other, not free text.

## Success criteria
- Pipeline runs end-to-end in under 10 seconds per claim.
- Fraud score is reproducible — same input, same score within a tolerance.
- Summary cites specific narrative spans; no invented timeline entries.

## Tradeoffs to discuss
- **Orchestration pattern.** Sequential with explicit state is the simplest
  path; a planner model routing between agents is more flexible but harder
  to debug.
- **LLM for classification vs. a small tuned model.** For volume, a small
  model is cheaper per call; for explainability, an LLM's reasoning chain is
  easier to review.
- **Human-in-the-loop gating.** Which outputs auto-proceed, which always
  require an adjuster's sign-off? Usually: approvals under $X auto-proceed,
  fraud referrals always require a human.

## What I'd do with more time
_Fill this in after building._
