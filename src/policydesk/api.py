from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI

from policydesk.auth import DemoTokenAuthenticator, bearer_header
from policydesk.config import load_config
from policydesk.ollama import OfflineGenerationClient
from policydesk.retrieval import BM25Index, load_policy_chunks
from policydesk.schemas import ApiAssistRequest, AssistRequest, AssistResponse
from policydesk.workflow import Assistant, load_orders


def create_app(root: Path = Path("."), ollama_client: object | None = None) -> FastAPI:
    state: dict[str, Assistant] = {}
    authenticator = DemoTokenAuthenticator.from_file(root / "fixtures/identities.json")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        config = load_config(root / "configs/app.yaml")
        assistant = Assistant(config, BM25Index(load_policy_chunks(root / "policies")), load_orders(root / "fixtures/orders.json"))
        if ollama_client is not None:
            assistant.ollama = ollama_client  # type: ignore[assignment]
        elif os.getenv("POLICYDESK_OFFLINE", "").lower() in {"1", "true", "yes"}:
            assistant.ollama = OfflineGenerationClient()  # type: ignore[assignment]
        state["assistant"] = assistant
        yield

    app = FastAPI(title="PolicyDesk", version="0.1.0", lifespan=lifespan)

    @app.get("/health/live")
    def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    def readiness() -> dict[str, object]:
        assistant = state.get("assistant")
        return {
            "status": "ready" if assistant else "not_ready",
            "retrieval_index_loaded": assistant is not None,
            # Local generation is optional, so its absence does not make the
            # deterministic service unready.
            "optional_generation_available": assistant.ollama.available() if assistant else False,
        }

    @app.post("/assist", response_model=AssistResponse)
    def assist(
        request: ApiAssistRequest,
        authorization: str | None = Depends(bearer_header),
    ) -> AssistResponse:
        identity = authenticator.authenticate(authorization)
        trusted_request = AssistRequest(
            ticket=request.ticket,
            order_id=request.order_id,
            customer_id=identity.customer_id,
        )
        return state["assistant"].assist(trusted_request)

    return app


app = create_app()
