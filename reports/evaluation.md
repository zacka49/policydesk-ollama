# Synthetic evaluation

Run on 24 September 2026 with 12 checked synthetic cases covering standard returns, the 30/31-day boundary, value review, ownership mismatch, missing order information, cancellation status, damage, payment, subscription, prompt injection and unclear intent.

| Measure | Result |
|---|---:|
| Deterministic decision accuracy | 12/12 (100%) |
| Required routing-status accuracy | 12/12 (100%) |
| Expected policy-document citation hit | 12/12 (100%) |
| Ollama-generated responses accepted | 9/12 |
| Deterministic fallbacks | 3/12 |

The benchmark is deliberately small and synthetic. Decision/routing checks are exact. The citation measure checks whether the expected document appears, but it is not a human judgement that every answer sentence is fully entailed. The model configuration was `llama3.2`, temperature 0; hardware and cold/warm latency should be recorded before publishing a latency claim.
