from __future__ import annotations

import json
from pathlib import Path

from policydesk.schemas import AssistRequest
from policydesk.workflow import Assistant


def run_evaluation(assistant: Assistant, cases_path: Path, output_path: Path) -> dict[str, object]:
    rows = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    for case in rows:
        response = assistant.assist(AssistRequest(ticket=case["ticket"], customer_id=case["customer_id"], order_id=case["order_id"]))
        cited_documents = {citation.document_id for citation in response.citations}
        expected_document = case["expected_document"]
        results.append({"case_id": case["case_id"], "decision_correct": response.decision == case["expected_decision"], "status_correct": response.status == case["expected_status"], "retrieval_hit": expected_document is None or expected_document in cited_documents, "generation_mode": response.generation_mode, "latency_ms": response.latency_ms})
    count = len(results)
    summary = {
        "cases": count,
        "decision_accuracy": sum(row["decision_correct"] for row in results) / count,
        "status_accuracy": sum(row["status_correct"] for row in results) / count,
        "retrieval_hit_rate": sum(row["retrieval_hit"] for row in results) / count,
        "fallback_cases": sum(row["generation_mode"] == "deterministic_fallback" for row in results),
        "limitations": "Synthetic policy benchmark; retrieval hit checks document identity, not full human citation support.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"summary": summary, "cases": results}, indent=2), encoding="utf-8")
    return summary

