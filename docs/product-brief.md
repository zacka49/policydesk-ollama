# Product brief

## User and decision

PolicyDesk helps a fictional Northstar Supplies support agent find the applicable policy and prepare the next response. The agent needs to decide whether to ask for information, draft a supported reply, or escalate. The application does not approve refunds or make payments.

## Baseline

The minimum useful baseline is deterministic intent routing, BM25 document retrieval and trusted Python policy rules. It remains available when local generation is unavailable. Any model-assisted path must beat or complement this baseline on a frozen evaluation without weakening decision, citation or authorisation controls.

## Error costs

The highest-cost failures are exposing another customer's order, changing a trusted eligibility decision, promising a financial outcome, citing evidence that was not retrieved, and confidently answering when required information is missing. These are release blockers. A missed relevant document or an unnecessary escalation is lower severity but still measured.

## Model contribution

The current optional model selects a subset of retrieved citations while consequential language remains deterministic. This is deliberately limited and should not be presented as proof that generation improves customer outcomes. The next experiment is a bounded multi-document summary or clarification task compared with the template baseline, using human claim-support review.

## Acceptance contract

- Server-derived identity is checked before an order is used.
- Trusted code owns decisions, statuses and consequential wording.
- Retrieved text and tickets are untrusted data.
- The deterministic path is the availability baseline.
- A candidate cannot ship with any regression in the authorisation/adversarial suite.
- Quality, latency and inference cost are reported separately.
