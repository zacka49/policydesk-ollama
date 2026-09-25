from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from pathlib import Path

import httpx

REQUESTS = [
    ("pd-demo-alice", {"ticket": "I want to return this order", "order_id": "NS-1001"}),
    ("pd-demo-alice", {"ticket": "The product arrived broken", "order_id": "NS-1001"}),
    ("pd-demo-bob", {"ticket": "Where is my late delivery?", "order_id": "NS-1004"}),
    ("pd-demo-bob", {"ticket": "Please return this order", "order_id": "NS-1001"}),
]


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * probability)))
    return ordered[index]


async def wait_until_live(base_url: str, timeout_seconds: float = 15) -> None:
    deadline = time.monotonic() + timeout_seconds
    async with httpx.AsyncClient(trust_env=False) as client:
        while time.monotonic() < deadline:
            try:
                response = await client.get(f"{base_url}/health/live", timeout=1)
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.2)
    raise RuntimeError(f"Service did not become live at {base_url}")


async def benchmark(base_url: str, request_count: int, concurrency: int, warmups: int) -> dict[str, object]:
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    timeout = httpx.Timeout(10)
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(limits=limits, timeout=timeout, trust_env=False) as client:
        async def send(index: int) -> tuple[float, int]:
            token, payload = REQUESTS[index % len(REQUESTS)]
            async with semaphore:
                started = time.perf_counter()
                response = await client.post(
                    f"{base_url}/assist",
                    headers={"Authorization": f"Bearer {token}"},
                    json=payload,
                )
                elapsed_ms = (time.perf_counter() - started) * 1000
                return elapsed_ms, response.status_code

        for index in range(warmups):
            _, status = await send(index)
            if status != 200:
                raise RuntimeError(f"Warmup failed with HTTP {status}")

        started = time.perf_counter()
        rows = await asyncio.gather(*(send(index) for index in range(request_count)))
        duration = time.perf_counter() - started

    latencies = [latency for latency, _ in rows]
    successes = sum(status == 200 for _, status in rows)
    return {
        "workload": {
            "base_url": base_url,
            "requests": request_count,
            "concurrency": concurrency,
            "warmups": warmups,
            "request_variants": len(REQUESTS),
            "generation": "deterministic unless the target service is configured otherwise",
        },
        "results": {
            "successes": successes,
            "errors": request_count - successes,
            "duration_seconds": round(duration, 4),
            "throughput_requests_per_second": round(request_count / duration, 2),
            "latency_mean_ms": round(statistics.mean(latencies), 3),
            "latency_p50_ms": round(percentile(latencies, 0.50), 3),
            "latency_p95_ms": round(percentile(latencies, 0.95), 3),
            "latency_p99_ms": round(percentile(latencies, 0.99), 3),
        },
        "limitations": [
            "Synthetic requests and identities; no customer traffic.",
            "A local run measures one machine and is not an availability or capacity claim.",
            "HTTP timings include the socket/service path but exclude browser and wide-area latency.",
        ],
    }


async def async_main(args: argparse.Namespace) -> dict[str, object]:
    process: asyncio.subprocess.Process | None = None
    try:
        if args.spawn:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "uvicorn",
                "policydesk.api:app",
                "--app-dir",
                "src",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.port),
                "--log-level",
                "warning",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                env={**os.environ, "POLICYDESK_OFFLINE": "1"},
            )
        await wait_until_live(args.base_url)
        return await benchmark(args.base_url, args.requests, args.concurrency, args.warmups)
    finally:
        if process is not None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except TimeoutError:
                process.kill()
                await process.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark PolicyDesk over a real HTTP socket")
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--warmups", type=int, default=10)
    parser.add_argument("--spawn", action="store_true", help="Start a local uvicorn process")
    parser.add_argument("--output", type=Path, default=Path("outputs/http-benchmark.json"))
    args = parser.parse_args()
    if args.requests <= 0 or args.concurrency <= 0 or args.warmups < 0:
        parser.error("requests/concurrency must be positive and warmups non-negative")
    result = asyncio.run(async_main(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
