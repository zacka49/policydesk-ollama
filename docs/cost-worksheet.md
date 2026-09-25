# Azure cost worksheet

Complete this worksheet with the Azure pricing calculator and subscription quota pages immediately before provisioning. Prices, free grants and regional availability change; this repository does not hard-code a cost claim.

Rates below were queried from the [Azure Retail Prices API](https://learn.microsoft.com/rest/api/cost-management/retail-prices/azure-retail-prices) in GBP for `uksouth` on 25 September 2026. They are public retail rates, not a quote for a particular subscription. The planned evidence run lasts no more than four hours and tears down the dedicated resource group the same day.

| Component | Planned setting | Retail rate observed | Four-hour evidence-run estimate | Observed cost |
|---|---|---:|---:|---:|
| Container Apps | Consumption environment; 0.5 vCPU, 1 GiB, 0–2 replicas, scale to zero | Environment management £0.092/hour; standard active vCPU/memory meters returned £0 at the queried tier | Up to £0.37 environment charge; verify subscription grants and meter applicability | Not deployed |
| Container Registry | Basic; one small image; delete with resource group | £0.1227/day plus £0.0736/GB-month | About £0.13 plus negligible storage | Not deployed |
| Log Analytics | 30-day retention; bounded synthetic traffic; target under 0.1 GB | £2.1204/GB ingestion and £0.0957/GB-month retention | Up to £0.22 at the 0.1 GB guardrail | Not deployed |
| Retrieval service | Not provisioned in this initial deterministic deployment | N/A | £0 | £0 |
| Relational database | Not provisioned in this initial deterministic deployment | N/A | £0 | £0 |
| Hosted inference | Not provisioned; deterministic mode only | N/A | £0 | £0 |

The arithmetic estimate is below £0.75 before taxes, exchange/subscription adjustments or unexpected meters. The proposed control is a **£5 maximum budget, pending explicit approval**, with a £2 budget alert, active Cost Management monitoring and same-day teardown after preserving evidence. The approved figure will be a task limit, not an Azure hard cap.

Record region, currency, calculator date, expected requests/day, log volume, run duration, budget alert threshold and teardown date. Treat an Azure budget alert as notification rather than a hard spending cap. Re-query rates immediately before deployment because the API rates can change.
