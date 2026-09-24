from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from policydesk.config import AppConfig


@dataclass(frozen=True)
class Decision:
    decision: str
    status: str
    reason_codes: tuple[str, ...]


def infer_intent(ticket: str) -> str:
    lowered = ticket.lower()
    keywords = [
        ("damaged_item", ("damaged", "broken", "cracked")),
        ("return_request", ("return", "send back", "refund")),
        ("cancel_order", ("cancel", "stop my order")),
        ("delivery_question", ("delivery", "late", "arrive", "tracking", "lost")),
        ("subscription_question", ("subscription", "renewal", "renew")),
        ("payment_question", ("payment", "card", "charge")),
        ("exchange_question", ("exchange", "replacement")),
        ("product_care", ("clean", "care", "wash")),
    ]
    return next((intent for intent, terms in keywords if any(term in lowered for term in terms)), "unknown")


def decide(intent: str, order: dict[str, object] | None, customer_id: str, config: AppConfig) -> Decision:
    if intent in {"return_request", "cancel_order", "delivery_question", "damaged_item"} and order is None:
        return Decision("missing_order", "ask_for_information", ("ORDER_REQUIRED",))
    if order is not None and str(order["customer_id"]) != customer_id:
        return Decision("unauthorised_order", "escalate", ("ORDER_OWNERSHIP_MISMATCH",))
    if intent == "return_request":
        assert order is not None
        if order["status"] != "delivered" or not order.get("delivery_date"):
            return Decision("not_returnable_status", "escalate", ("ORDER_NOT_DELIVERED",))
        delivery_date = date.fromisoformat(str(order["delivery_date"]))
        days = (config.clock - delivery_date).days
        if days < 0:
            return Decision("invalid_delivery_date", "escalate", ("DELIVERY_DATE_IN_FUTURE",))
        if days > config.returns.standard_window_days:
            return Decision("outside_return_window", "escalate", ("OUTSIDE_RETURN_WINDOW",))
        if float(order["order_value_gbp"]) > config.returns.max_order_value_for_draft_gbp:
            return Decision("high_value_review", "escalate", ("VALUE_REQUIRES_REVIEW",))
        return Decision("eligible_for_review", "draft", ("WITHIN_WINDOW", "VALUE_WITHIN_LIMIT"))
    if intent == "cancel_order":
        assert order is not None
        return Decision("cancellable" if order["status"] == "processing" else "cannot_auto_cancel", "draft" if order["status"] == "processing" else "escalate", ("PROCESSING_ORDER",) if order["status"] == "processing" else ("ORDER_ALREADY_PROGRESSING",))
    if intent == "damaged_item":
        return Decision("damage_review", "escalate", ("EVIDENCE_AND_HUMAN_REVIEW",))
    if intent == "unknown":
        return Decision("unsupported_intent", "ask_for_information", ("INTENT_UNCLEAR",))
    return Decision("policy_answer", "draft", ("POLICY_EVIDENCE_AVAILABLE",))

