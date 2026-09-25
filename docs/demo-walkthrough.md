# PolicyDesk: three-minute walkthrough

## Audience and decision

PolicyDesk is a fictional retail-support assistant. It helps an agent find policy evidence and draft a response while keeping eligibility and monetary decisions in trusted code. The demonstration is synthetic and does not claim customer use.

## Before the recording

```powershell
uv sync --extra dev --extra mcp
uv run pytest -q
uv run policydesk evaluate --offline
uv run policydesk serve
```

## Recording script

**0:00–0:30 — Frame the risk.** Show the architecture image in the README. Explain that ticket text and retrieved documents are untrusted, identity is derived on the server, and Python owns the consequential decision.

**0:30–1:15 — Exercise the happy path.** Submit `NS-1001` with the `pd-demo-alice` bearer identity. Point out the retrieved citations, trusted status and deterministic fallback. Mention that optional generation can select supporting evidence but cannot rewrite the decision.

**1:15–1:50 — Exercise a boundary.** Repeat with another customer's order or a client-supplied customer identifier. Show the rejected access and explain why protected data never enters model context.

**1:50–2:25 — Show measured evidence.** Open `reports/evaluation-v2.md`: 22/22 decisions, 20/20 expected document hits and 0.808 MRR@4. Open `reports/local-http-benchmark.md`: 250/250 real-socket responses. State that the workload is local and synthetic.

**2:25–3:00 — Show delivery judgment.** Open `docs/azure-deployment.md`, the Bicep templates and the manual OIDC workflow. Explain that these are deployment-ready artifacts and that no Azure result is claimed until the workflow, alert and rollback drill have actually run.

## Interview prompts this supports

- Why keep deterministic rules beside a language model?
- Where is authorisation enforced, and what reaches model context?
- How would you compare BM25, dense and hybrid retrieval fairly?
- What evidence would be required before production promotion?
