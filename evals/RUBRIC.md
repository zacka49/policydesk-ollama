# Evaluation rubric

The checked-in suite is authored synthetic data. Cases cover core routing, boundaries, cross-customer access, prompt injection, policy conflicts, ambiguity and retrieval paraphrases.

- **Decision correct:** exact match to the trusted rule outcome defined before the run.
- **Status correct:** exact match to draft, ask-for-information or escalate.
- **Retrieval recall@k:** the expected policy document appears in the positive-score top-k set. Cases with no expected document are excluded.
- **MRR@k:** reciprocal rank of the expected policy document in the same set.
- **Claim support:** requires manual sentence-level review and is not inferred from a valid citation identifier.
- **Authorisation:** API cases must derive the customer from the bearer identity; missing/invalid tokens, missing scopes and client-supplied identity are rejected.

The final test set should be locked before comparing a learned retrieval or generation candidate. This small suite is a development baseline and should not be described as representative customer traffic.
