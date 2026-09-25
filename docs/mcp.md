# MCP integration

PolicyDesk exposes a genuine local MCP stdio server through the official Python SDK. The server supports protocol initialisation, tool discovery and calls for `search_policy`, `lookup_order`, and `create_support_draft`.

Install the optional dependency and launch it with a fictional identity fixed in the server process:

```powershell
uv sync --extra dev --extra mcp
$env:POLICYDESK_MCP_BEARER_TOKEN = "pd-demo-alice"
$env:POLICYDESK_ROOT = (Get-Location).Path
$env:POLICYDESK_OFFLINE = "1"
uv run policydesk-mcp
```

Customer identity is not a tool argument. Order lookup returns the same generic result for missing and forbidden identifiers. Draft creation requires an operation ID, replays an identical request safely, and rejects reuse for different inputs. Decisions and consequential wording remain in trusted application code.

The automated integration test starts two independent stdio client/server sessions, performs MCP initialisation and discovery, and proves that Alice can access her synthetic order while Bob receives the generic forbidden/not-found response.

This is local stdio evidence. It does not claim remote MCP authentication. A remote transport would require validated audience/scopes, HTTPS, origin controls where applicable, SSRF protections, and a ban on token passthrough. Static fixture tokens remain unsuitable for real data.
