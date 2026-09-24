from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from policydesk.config import load_config
from policydesk.evaluate import run_evaluation
from policydesk.retrieval import BM25Index, load_policy_chunks
from policydesk.schemas import AssistRequest
from policydesk.workflow import Assistant, load_orders


def build_assistant(root: Path) -> Assistant:
    return Assistant(load_config(root / "configs/app.yaml"), BM25Index(load_policy_chunks(root / "policies")), load_orders(root / "fixtures/orders.json"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PolicyDesk")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--ticket", default="I want to return this order")
    demo.add_argument("--customer", default="C-001")
    demo.add_argument("--order", default="NS-1001")
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--cases", type=Path, default=Path("evals/test_cases.jsonl"))
    evaluate.add_argument("--output", type=Path, default=Path("outputs/evaluation.json"))
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "serve":
        uvicorn.run("policydesk.api:app", host=args.host, port=args.port, reload=False)
        return
    assistant = build_assistant(Path("."))
    if args.command == "demo":
        result = assistant.assist(AssistRequest(ticket=args.ticket, customer_id=args.customer, order_id=args.order))
        print(result.model_dump_json(indent=2))
    else:
        print(json.dumps(run_evaluation(assistant, args.cases, args.output), indent=2))


if __name__ == "__main__":
    main()

