# Scenario 06 — Cross-Product Customer 360

## Business pain point
A relationship manager serving a high-net-worth household wants a unified view
across the institution's product lines: retail deposits, any active loans, any
wealth advisory relationship, any insurance policies, any open service
issues. Today that view lives in five different systems.

## What to build
An agent that, given an entity (retail customer ID, wealth client ID, or a
fuzzy name), returns a structured 360° view:

- Retail footprint: accounts, recent transactions, service tickets.
- Lending footprint: any matched loan records.
- Wealth footprint: advisor, AUM, open KYC flags.
- Insurance footprint: active claims, policy count.
- Overall "relationship temperature": one-paragraph qualitative read.

Because the seed data doesn't link entities across domains, the agent must
handle missing joins gracefully — absence of evidence in one domain should be
explicit, not hidden.

## Success criteria
- View assembles in under 5 seconds.
- Every section states "no matching records" when empty, rather than
  omitting.
- Fuzzy name match surfaces candidate entities with confidence scores
  rather than silently picking one.

## Tradeoffs to discuss
- **Entity resolution.** Names alone are unreliable; in a real system you'd
  lean on deterministic IDs (tax ID, household ID) plus fuzzy match as
  fallback. Here, show the fallback clearly.
- **Caching.** A relationship manager dashboard is read-heavy; cached
  aggregates are appropriate but must invalidate on ticket updates.
- **Privacy scope.** Some views (KYC flags) may not be visible to all
  relationship manager tiers. Where does the authorization check live —
  at the data layer, the agent layer, or the UI?

## What I'd do with more time
_Fill this in after building._
