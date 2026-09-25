from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    document_id: str
    chunk_id: str


class DraftResponse(BaseModel):
    status: Literal["draft", "ask_for_information", "escalate"]
    intent: str
    answer: str = Field(min_length=1, max_length=2000)
    citations: list[Citation]


class AssistRequest(BaseModel):
    ticket: str = Field(min_length=3, max_length=3000)
    customer_id: str = Field(min_length=1, max_length=100)
    order_id: str | None = Field(default=None, max_length=100)


class ApiAssistRequest(BaseModel):
    """Public request body. Customer identity comes from authentication."""

    model_config = ConfigDict(extra="forbid")

    ticket: str = Field(min_length=3, max_length=3000)
    order_id: str | None = Field(default=None, max_length=100)


class AssistResponse(DraftResponse):
    request_id: str
    decision: str
    reason_codes: list[str]
    policy_version: str
    generation_mode: Literal["ollama", "deterministic_fallback"]
    latency_ms: float
