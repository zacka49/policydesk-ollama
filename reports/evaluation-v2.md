# Deterministic baseline evaluation v2

Run on 25 September 2026 with:

```powershell
uv run policydesk evaluate --offline --output outputs/evaluation-v2.json
```

| Measure | Result |
|---|---:|
| Cases | 22 |
| Trusted decision accuracy | 22/22 (100%) |
| Routing status accuracy | 22/22 (100%) |
| Retrieval cases | 20 |
| Document recall@4 | 20/20 (100%) |
| Document MRR@4 | 0.8083 |
| Deterministic fallback cases | 22/22 |
| Local in-process p50 | 0.101 ms |
| Local in-process p95 | 0.137 ms |

The suite adds cross-customer, prompt-injection, policy-conflict, boundary, ambiguity and paraphrase cases to the original core set. API security has separate integration tests for missing/invalid authority, scope, server-derived identity and client-supplied identity.

These are authored synthetic policies, orders and cases. Document retrieval metrics do not establish sentence-level citation support or performance on real customer language. The timing excludes HTTP/network overhead and model generation, so it is not a serving benchmark. The offline run measures the deterministic availability baseline; it does not demonstrate model benefit.

The JSON output is generated locally and is not checked in because it includes run-specific timing. The cases and scoring implementation are versioned.
