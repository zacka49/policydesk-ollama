from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import httpx

from policydesk.config import AppConfig
from policydesk.ollama import OllamaClient, build_prompt
from policydesk.retrieval import BM25Index
from policydesk.rules import Decision, decide, infer_intent
from policydesk.schemas import AssistRequest, AssistResponse, Citation, DraftResponse


def load_orders(path: Path) -> dict[str, dict[str, object]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {str(row["order_id"]): row for row in rows}


def fallback_draft(intent: str, decision: Decision, evidence: list[dict[str, str]]) -> DraftResponse:
    messages = {
        "eligible_for_review": "The order is within the standard return window and value threshold. A support agent can review the return route; this is not confirmation of a refund.",
        "outside_return_window": "The order is outside the standard return window, so this request needs human review.",
        "high_value_review": "This order exceeds the automatic draft threshold and needs human review.",
        "missing_order": "Please provide the order number so the request can be checked.",
        "unauthorised_order": "This order cannot be accessed for the authenticated customer. A support agent must review the request.",
        "cancellable": "The order is still processing and can follow the cancellation route.",
        "cannot_auto_cancel": "The order has progressed beyond processing and cannot be cancelled automatically.",
        "damage_review": "Please describe the damage and provide a photograph when practical. A human agent will review the claim.",
        "unsupported_intent": "Please provide more detail about the help you need.",
        "policy_answer": "The relevant policy evidence is shown below for a support agent to review.",
        "not_returnable_status": "The order is not recorded as delivered, so the standard return rule cannot be applied.",
        "invalid_delivery_date": "The recorded delivery date is inconsistent and requires human review.",
    }
    citations = [Citation(document_id=row["document_id"], chunk_id=row["chunk_id"]) for row in evidence]
    return DraftResponse(status=decision.status, intent=intent, answer=messages[decision.decision], citations=citations)


class Assistant:
    def __init__(self, config: AppConfig, index: BM25Index, orders: dict[str, dict[str, object]], ollama: OllamaClient | None = None):
        self.config, self.index, self.orders = config, index, orders
        self.ollama = ollama or OllamaClient(config.generation)

    def assist(self, request: AssistRequest) -> AssistResponse:
        started = perf_counter()
        intent = infer_intent(request.ticket)
        order = self.orders.get(request.order_id) if request.order_id else None
        decision = decide(intent, order, request.customer_id, self.config)
        retrieved = self.index.search(f"{intent} {request.ticket}", self.config.retrieval.top_k)
        evidence = [{"document_id": chunk.document_id, "chunk_id": chunk.chunk_id, "title": chunk.title, "text": chunk.text} for chunk, _ in retrieved if _ > 0]
        draft = fallback_draft(intent, decision, evidence)
        mode = "deterministic_fallback"
        if evidence and self.ollama.available():
            try:
                candidate = self.ollama.draft(build_prompt(request.ticket, intent, decision.decision, decision.status, decision.reason_codes, evidence))
                valid_ids = {(row["document_id"], row["chunk_id"]) for row in evidence}
                citations_valid = all((citation.document_id, citation.chunk_id) in valid_ids for citation in candidate.citations)
                if candidate.status == decision.status and candidate.intent == intent and citations_valid:
                    unique: dict[tuple[str, str], Citation] = {}
                    for citation in candidate.citations:
                        unique.setdefault((citation.document_id, citation.chunk_id), citation)
                    candidate.citations = list(unique.values())[: self.config.retrieval.top_k]
                    draft, mode = candidate, "ollama"
            except (httpx.HTTPError, ValueError, KeyError):
                pass
        return AssistResponse(
            request_id=str(uuid4()),
            **draft.model_dump(),
            decision=decision.decision,
            reason_codes=list(decision.reason_codes),
            policy_version=self.config.policy_version,
            generation_mode=mode,
            latency_ms=round((perf_counter() - started) * 1000, 3),
        )
