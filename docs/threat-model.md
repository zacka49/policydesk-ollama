# Threat model

PolicyDesk is a synthetic portfolio service. The static bearer-token fixture demonstrates where authenticated identity enters the application; it is not a production identity provider.

| Asset or boundary | Main threat | Current control | Required deployment control |
|---|---|---|---|
| Order records | Cross-customer disclosure | Bearer token maps to a customer on the server; ownership checked before a decision | Validate OIDC issuer, audience, expiry and scopes; enforce tenant and subject mapping in the data query |
| Policy decision | Ticket or model changes eligibility | Deterministic Python rules and immutable decision/status in the response path | Version rules and release them atomically with compatible policy/index versions |
| Generated text | Unsupported promise or invented evidence | Consequential answer is templated; citations must be a non-empty subset of retrieval | Claim-level support review and monitored model/version release gates |
| Retrieved content | Prompt injection | Prompt labels evidence as untrusted; generated answer cannot replace the trusted template | Content provenance, audience filtering and adversarial retrieval tests |
| Credentials | Token or secret disclosure | Only fictional tokens are checked in; no application logs contain them | Managed identity/secret store and structured redaction |
| Service health | Dependency outage restarts healthy service | Liveness has no dependency call; readiness reports optional generation separately | Dependency metrics, timeouts, alerts and tested rollback |

## Explicit non-goals

The fixture authenticator does not implement signing, expiry, revocation, federation or secure token storage. The JSON order store is not a substitute for row-level tenant enforcement. These controls must be replaced before any real customer data is connected.
