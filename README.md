# Forge Tool 🔨

> **⚠️ ALPHA — Still testing. Export your agent backup before installing. See postit-tool for known issues.**

**A Letta tool that lets agents create their own tools at runtime.**

Give an agent this tool and it can extend its own capabilities — create new tools, attach them, update them, and detach them. The agent looks at a problem, realizes it needs a new tool, writes it, creates it, and uses it.

## What It Does

`forge_tool` lets the agent:
1. **Create** a new tool from Python source code and auto-attach it
2. **Update** an existing tool's description or code (this is how post-it notes get written)
3. **Attach** a previously detached tool back into context
4. **Detach** a tool from context (data stays on server)
5. **List** currently attached tools

All attach/detach operations are **safe** — they read the current tool list first and append/remove, never replace. This prevents the accidental wipe that raw PATCH causes.

## Install via ADE

1. **Export your agent first** (backup!)
2. Copy the code from [`forge_tool.py`](https://github.com/audrebytes/forge-tool/blob/main/forge_tool.py)
3. Open your agent in ADE
4. Go to the tool creation screen
5. Paste the code
6. Save and attach to your agent

The tool automatically picks up `LETTA_API_KEY` and `LETTA_AGENT_ID` from the sandbox environment — no configuration needed.

## Install via SDK

```python
from letta_client import Letta

client = Letta()

# Read the source from forge_tool.py, or paste it inline
with open("forge_tool.py") as f:
    source = f.read()

tool = client.tools.create(source_code=source)
client.agents.tools.attach(agent_id="YOUR_AGENT_ID", tool_id=tool.id)
```

## The Code

See **[`forge_tool.py`](https://github.com/audrebytes/forge-tool/blob/main/forge_tool.py)** in this repo. It's a single Python function, ready to copy-paste into the ADE tool creation screen. All imports are inside the function body (sandbox requirement).

## Use Cases

### Post-it notes (detachable working memory)
Agent creates a tool whose description holds working state. Detach to free context, reattach to get it back. See [postit-tool](https://github.com/audrebytes/postit-tool).

### Web fetcher
Agent needs to check a URL mid-task:
```python
def fetch_url(url: str) -> str:
    """Fetch a web page and return its text content."""
    import requests
    resp = requests.get(url, timeout=10)
    return resp.text[:5000]
```

### Data format converter
Agent is processing data and needs to convert between formats:
```python
def json_to_csv(json_data: str) -> str:
    """Convert a JSON array to CSV."""
    import json, csv, io
    data = json.loads(json_data)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()
```

### Webhook notifier
Agent wants to ping a Slack or Discord channel:
```python
def notify_discord(webhook_url: str, message: str) -> str:
    """Send a message to a Discord webhook."""
    import requests
    resp = requests.post(webhook_url, json={"content": message})
    return f"Sent: {resp.status_code}"
```

### Domain-specific calculator
Agent is doing financial analysis and builds what it needs:
```python
def compound_interest(principal: float, rate: float, years: int) -> str:
    """Calculate compound interest."""
    result = principal * (1 + rate) ** years
    return f"${result:,.2f}"
```

The pattern: agent hits a wall, realizes it needs a capability it doesn't have, writes it, creates it, uses it. The agent adapts to the task instead of the task being limited to pre-configured tools.

## ⚠️ Security Note

This tool gives the agent the ability to create arbitrary Python code and attach it as executable tools. This is powerful but carries risk:

- **Only give forge-tool to trusted agents.** An agent with this tool can create any tool it wants.
- **Custom tools execute in a sandbox** with network access and scoped API credentials.
- **Export your agent before installing.** If something goes wrong, you have a recovery path.

## Related

- [postit-tool](https://github.com/audrebytes/postit-tool) — Detachable working memory using forge-tool to create storage tools
- [hold-my-beer](https://github.com/audrebytes/hold-my-beer) — File-based working memory for agents with filesystem access

---

*Created by Forge & Aeo, February 2026.*
*Part of the [symbio.quest](https://symbio.quest) research infrastructure.*
