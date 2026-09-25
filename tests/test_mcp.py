import asyncio
import os
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from policydesk.mcp_server import PolicyDeskMCPService

ROOT = Path(__file__).resolve().parents[1]


def test_mcp_service_enforces_identity_and_idempotency() -> None:
    alice = PolicyDeskMCPService(ROOT, "pd-demo-alice")
    bob = PolicyDeskMCPService(ROOT, "pd-demo-bob")

    assert alice.lookup_order("NS-1001")["status"] == "found"
    assert bob.lookup_order("NS-1001")["status"] == "not_found_or_forbidden"

    first = alice.create_support_draft("Return this order", "NS-1001", "op-1")
    replay = alice.create_support_draft("Return this order", "NS-1001", "op-1")
    assert not first["idempotent_replay"]
    assert replay["idempotent_replay"]
    assert replay["draft"]["decision"] == "eligible_for_review"

    with pytest.raises(ValueError, match="different request"):
        alice.create_support_draft("Cancel this order", "NS-1001", "op-1")


async def _inspect_server(token: str, order_id: str) -> tuple[set[str], str]:
    environment = {
        **os.environ,
        "POLICYDESK_MCP_BEARER_TOKEN": token,
        "POLICYDESK_ROOT": str(ROOT),
        "POLICYDESK_OFFLINE": "1",
        "PYTHONPATH": str(ROOT / "src"),
    }
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "policydesk.mcp_server"],
        env=environment,
        cwd=ROOT,
    )
    async with stdio_client(parameters) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        listing = await session.list_tools()
        result = await session.call_tool("lookup_order", {"order_id": order_id})
        assert result.structuredContent is not None
        return {tool.name for tool in listing.tools}, str(result.structuredContent["status"])


def test_real_mcp_lifecycle_and_two_independent_clients() -> None:
    async def run() -> None:
        alice_tools, alice_status = await _inspect_server("pd-demo-alice", "NS-1001")
        bob_tools, bob_status = await _inspect_server("pd-demo-bob", "NS-1001")
        assert alice_tools == {"search_policy", "lookup_order", "create_support_draft"}
        assert bob_tools == alice_tools
        assert alice_status == "found"
        assert bob_status == "not_found_or_forbidden"

    asyncio.run(run())
