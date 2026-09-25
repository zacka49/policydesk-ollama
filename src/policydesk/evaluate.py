from __future__ import annotations

import json
import math
from pathlib import Path

from policydesk.rules import infer_intent
from policydesk.schemas import AssistRequest
from policydesk.workflow import Assistant


def run_evaluation(assistant: Assistant, cases_path: Path, output_path: Path) -> dict[str, object]:
    rows = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    for case in rows:
        response = assistant.assist(AssistRequest(ticket=case["ticket"], customer_id=case["customer_id"], order_id=case["order_id"]))
        cited_documents = {citation.document_id for citation in response.citations}
        expected_document = case["expected_document"]
        intent = infer_intent(case["ticket"])
        ranking = assistant.index.search(
            f"{intent} {case['ticket']}", assistant.config.retrieval.top_k
        )
        ranked_documents = [chunk.document_id for chunk, score in ranking if score > 0]
        expected_rank = (
            ranked_documents.index(expected_document) + 1
            if expected_document in ranked_documents
            else None
        )
        results.append(
            {
                "case_id": case["case_id"],
                "category": case.get("category", "core"),
                "decision_correct": response.decision == case["expected_decision"],
                "status_correct": response.status == case["expected_status"],
                "retrieval_hit": expected_document is None or expected_document in cited_documents,
                "expected_document_rank": expected_rank,
                "reciprocal_rank": (
                    1.0 if expected_document is None else 1.0 / expected_rank if expected_rank else 0.0
                ),
                "generation_mode": response.generation_mode,
                "latency_ms": response.latency_ms,
            }
        )
    count = len(results)
    retrieval_rows = [row for row, case in zip(results, rows, strict=True) if case["expected_document"] is not None]
    latencies = sorted(float(row["latency_ms"]) for row in results)
    p95_index = max(0, math.ceil(0.95 * len(latencies)) - 1)
    summary = {
        "cases": count,
        "decision_accuracy": sum(row["decision_correct"] for row in results) / count,
        "status_accuracy": sum(row["status_correct"] for row in results) / count,
        "retrieval_cases": len(retrieval_rows),
        "retrieval_recall_at_k": sum(row["retrieval_hit"] for row in retrieval_rows) / len(retrieval_rows),
        "retrieval_mrr_at_k": sum(row["reciprocal_rank"] for row in retrieval_rows) / len(retrieval_rows),
        "fallback_cases": sum(row["generation_mode"] == "deterministic_fallback" for row in results),
        "latency_p50_ms": latencies[len(latencies) // 2],
        "latency_p95_ms": latencies[p95_index],
        "limitations": (
            "Synthetic authored-policy benchmark. Document retrieval metrics do not prove "
            "claim-level citation support or real customer performance."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"summary": summary, "cases": results}, indent=2), encoding="utf-8")
    return summary
