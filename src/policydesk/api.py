from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from policydesk.config import load_config
from policydesk.retrieval import BM25Index, load_policy_chunks
from policydesk.schemas import AssistRequest, AssistResponse
from policydesk.workflow import Assistant, load_orders


def create_app(root: Path = Path("."), ollama_client: object | None = None) -> FastAPI:
    state: dict[str, Assistant] = {}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        config = load_config(root / "configs/app.yaml")
        assistant = Assistant(config, BM25Index(load_policy_chunks(root / "policies")), load_orders(root / "fixtures/orders.json"))
        if ollama_client is not None:
            assistant.ollama = ollama_client  # type: ignore[assignment]
        state["assistant"] = assistant
        yield

    app = FastAPI(title="PolicyDesk", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, object]:
        assistant = state.get("assistant")
        return {"status": "ok" if assistant else "not_ready", "ollama_available": assistant.ollama.available() if assistant else False}

    @app.post("/assist", response_model=AssistResponse)
    def assist(request: AssistRequest) -> AssistResponse:
        return state["assistant"].assist(request)

    return app


app = create_app()
