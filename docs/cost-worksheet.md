# Azure cost worksheet

Complete this worksheet with the Azure pricing calculator and subscription quota pages immediately before provisioning. Prices, free grants and regional availability change; this repository does not hard-code a cost claim.

| Component | Planned setting | Current price source checked | Estimated monthly maximum | Observed cost |
|---|---|---|---:|---:|
| Container Apps | 0.5 vCPU, 1 GiB, 0–2 replicas, scale to zero | Pending | Pending | Not deployed |
| Container Registry | Basic; short retention for demo images | Pending | Pending | Not deployed |
| Log Analytics | 30-day retention; bounded synthetic traffic | Pending | Pending | Not deployed |
| Retrieval service | Not provisioned in this initial deterministic deployment | N/A | £0 | £0 |
| Relational database | Not provisioned in this initial deterministic deployment | N/A | £0 | £0 |
| Hosted inference | Not provisioned; deterministic mode only | N/A | £0 | £0 |

Record region, currency, calculator date, expected requests/day, log volume, run duration, budget alert threshold and teardown date. Treat an Azure budget alert as notification rather than a hard spending cap.
