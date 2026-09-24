# PolicyDesk

PolicyDesk is a local, evidence-grounded support assistant for a fictional retailer. It retrieves versioned policy text, performs an authorised read-only order lookup, computes policy decisions in trusted Python, and optionally asks Ollama to draft a schema-validated response around that immutable decision.

It works without Ollama using a deterministic fallback. When Ollama is serving at `http://127.0.0.1:11434`, PolicyDesk uses the configured local model and rejects generated responses that change the required status or cite evidence that was not retrieved.

## Quick start

```powershell
uv sync --extra dev
uv run policydesk demo
uv run policydesk evaluate
uv run pytest
uv run policydesk serve
```

The API can also run in Docker. On Windows, `host.docker.internal` is not the current default Ollama URL, so the container will use its deterministic fallback unless you expose/configure the Ollama endpoint in code or networking:

```powershell
docker build -t policydesk .
docker run --rm -p 8000:8000 policydesk
```

API example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/assist -Method Post -ContentType application/json -Body '{"ticket":"I want to return this order","customer_id":"C-001","order_id":"NS-1001"}'
```

To use Ollama, start its service and ensure the model in `configs/app.yaml` is installed. For example, if `ollama` is on your PATH:

```powershell
ollama serve
ollama pull llama3.2
```

## Reliability design

```text
ticket + authenticated demo customer
  -> intent + BM25 policy retrieval
  -> authorised order lookup
  -> deterministic policy decision
  -> Ollama structured draft (when available)
  -> citation/status validation
  -> safe deterministic fallback
```

- Ticket text cannot change order ownership, dates, value, or rule thresholds.
- The model drafts language; Python decides return/cancellation routing.
- Unknown orders ask for information and ownership mismatches escalate.
- Missing/invalid model output falls back rather than inventing an answer.
- The included evaluation reports decision accuracy, status accuracy and policy-document retrieval hits across synthetic cases.

## Honest scope

The policies, orders, identities and benchmark are synthetic. This is not legal advice and is not connected to a real support system. A document-level retrieval hit does not prove every sentence is supported; add a blinded human citation-support audit before making a stronger quality claim. The API's customer ID simulates an authenticated context and must not be treated as real authentication.

The next useful additions are Ollama embedding retrieval, a larger held-out paraphrase set, and manually scored citation support. The current version deliberately keeps the workflow explicit and testable.

The current [synthetic evaluation](reports/evaluation.md) records 12/12 deterministic decisions, 12/12 routing statuses, 12/12 expected document hits, and which responses required fallback.
