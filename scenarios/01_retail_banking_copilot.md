# Scenario 01 — Retail Banking CSR Copilot

## Business pain point
Customer service reps (CSRs) at a mid-size retail bank juggle three internal
systems to answer a single caller question: core banking, the ticketing
platform, and a knowledge base. Median handle time sits around 8 minutes;
leadership has asked for a copilot that surfaces customer context and
recommended next steps in under 5 seconds.

## What to build
Given a caller's customer ID, build an agent that returns:

1. A one-paragraph summary of the customer (segment, tenure, recent activity).
2. The three most recent open/escalated tickets with short summaries.
3. Any anomalous transactions (flagged or over a threshold) in the last 30 days.
4. A suggested opening line the CSR can use to acknowledge the caller's history.

Use the `/customers/{id}` endpoint for data, and either an LLM call or a
deterministic summarizer for the synthesis step.

## Success criteria
- End-to-end response under 3 seconds on a warm cache.
- Copilot output references concrete ticket IDs and transaction amounts
  (no hallucinated numbers).
- Handles the "new customer, no tickets" edge case gracefully.

## Tradeoffs to discuss
- **Full context window vs. structured slots.** Dumping the whole customer
  record into the prompt is easy but expensive and leaks prompt-injection
  surface. Structured summaries are harder to build but safer.
- **LLM summary vs. templated extract.** For a 5-sec SLA the templated
  path is cheaper; LLM is warranted when free-text tickets need semantic
  compression.
- **Grounding.** How do you guarantee the model doesn't invent a ticket
  that isn't there? Post-hoc ID verification against the returned payload
  is the usual answer.

## What I'd do with more time
_Fill this in after building: latency numbers, token cost per call, the
one design choice you'd revisit._
