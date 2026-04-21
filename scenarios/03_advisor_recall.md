# Scenario 03 — Wealth Advisor Recall

## Business pain point
Wealth advisors walk into client calls cold. Meeting notes are scattered, some
are transcripts, some are bullet points. Advisors want a 90-second "catch me
up" brief before every call: what did we discuss last, what was the client's
mood, what did we promise to follow up on?

## What to build
Given a wealth client ID, produce a structured brief:

1. Last 3–5 meeting summaries, one sentence each.
2. Open action items (things advisor promised).
3. Sentiment trajectory (improving / steady / cooling).
4. One conversation starter grounded in the most recent note.

Use `GET /wealth/{id}` for notes and KYC flags; use an LLM to synthesize. Any
KYC/AML flags should be surfaced prominently — advisors must see them before
talking to the client.

## Success criteria
- Brief fits in a single screen, readable in 30 seconds.
- Action items are extracted verbatim where possible; sentiment is justified
  by a short quote.
- KYC flags with severity ≥ "medium" cannot be hidden by the summarizer.

## Tradeoffs to discuss
- **Free-form summary vs. structured JSON.** JSON is easier to render in a
  CRM; free-form reads better. A schema-constrained model output is a
  decent compromise.
- **Sentiment as a classifier vs. LLM judgment.** A small classifier is
  cheaper and more auditable; an LLM handles nuance better but needs
  calibration.
- **Hallucinated promises.** The single scariest failure mode — model
  invents a follow-up that wasn't actually promised. Mitigations: source
  spans, strict extraction prompts, post-hoc verification against the note
  text.

## What I'd do with more time
_Fill this in after building._
