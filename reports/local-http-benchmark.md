# Local deterministic HTTP workload

Run on 25 September 2026:

```powershell
uv run python scripts/benchmark_http.py --spawn --port 8899 --base-url http://127.0.0.1:8899 --requests 250 --concurrency 10 --warmups 20
```

| Measure | Result |
|---|---:|
| Requests | 250 |
| Concurrent requests | 10 |
| Warmups | 20 |
| Request variants | 4 |
| Successful responses | 250/250 |
| Duration | 2.4914 s |
| Throughput | 100.35 requests/s |
| Mean latency | 95.936 ms |
| p50 latency | 59.589 ms |
| p95 latency | 237.100 ms |
| p99 latency | 239.075 ms |

The script starts Uvicorn and sends requests through a real local HTTP socket. Generation was explicitly disabled so the run measures the deterministic application path. Inputs include ordinary returns/damage/delivery requests and a cross-customer order that must route safely.

These are synthetic requests and identities on one development machine. This is not a production capacity, availability or wide-area latency claim. The run did not measure a hosted model, Azure networking, cold container starts or cloud cost. Re-run the same declared workload against a deployed candidate before making a cloud-serving claim.
