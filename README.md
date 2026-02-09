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
2. Open your agent in ADE
3. Go to the tool creation screen
4. Paste the contents of `forge_tool.py` from this repo
5. Save and attach to your agent

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

See **`forge_tool.py`** in this repo. It's a single Python function, ready to copy-paste into the ADE tool creation screen. All imports are inside the function body (sandbox requirement).

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
