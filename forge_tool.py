def forge_tool(action: str, name: str = None, source_code: str = None,
               tool_id: str = None, description: str = None) -> str:
    """Create, update, attach, detach, or list tools at runtime. Uses the calling agent's own credentials and ID automatically.

    Args:
        action: One of "create", "update", "attach", "detach", "list". Create makes a new tool and attaches it to you. Update changes an existing tool's description or code. Detach removes a tool from your context (data persists on server). Attach reattaches a previously detached tool. List shows your current tools.
        name: Informational only — the actual tool name comes from the function name in source_code (used with "create").
        source_code: Python source code defining a single function with docstring. All imports MUST be inside the function body (used with "create").
        tool_id: ID of an existing tool (used with "update", "attach", "detach").
        description: Tool description text — this is where post-it data lives (used with "update").

    Returns:
        Result of the operation including tool IDs for future reference.
    """
    import requests
    import json
    import os

    api_key = os.environ.get("LETTA_API_KEY", "")
    agent_id = os.environ.get("LETTA_AGENT_ID", "")
    base = "https://api.letta.com/v1"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    if not api_key:
        return "Error: LETTA_API_KEY not found in environment"
    if not agent_id and action in ("create", "attach", "detach", "list"):
        return "Error: LETTA_AGENT_ID not found in environment"

    if action == "create":
        if not source_code:
            return "Error: source_code required for create"
        resp = requests.post(f"{base}/tools/", headers=headers, json={"source_code": source_code})
        if resp.status_code != 200:
            return f"Create failed: {resp.status_code} {resp.text[:300]}"
        tool = resp.json()
        new_tool_id = tool["id"]
        # SAFE ATTACH: read current tools first, then append
        agent_resp = requests.get(f"{base}/agents/{agent_id}", headers=headers)
        if agent_resp.status_code != 200:
            return f"Created {tool['name']} ({new_tool_id}) but could not read agent to attach: {agent_resp.status_code}"
        current_tool_ids = [t["id"] for t in agent_resp.json().get("tools", [])]
        current_tool_ids.append(new_tool_id)
        attach_resp = requests.patch(f"{base}/agents/{agent_id}", headers=headers, json={"tool_ids": current_tool_ids})
        if attach_resp.status_code == 200:
            return f"Created and attached: {tool['name']} ({new_tool_id})"
        return f"Created {tool['name']} ({new_tool_id}) but attach failed: {attach_resp.status_code}"

    elif action == "update":
        if not tool_id:
            return "Error: tool_id required for update"
        payload = {}
        if source_code:
            payload["source_code"] = source_code
        if description:
            payload["description"] = description
        if not payload:
            return "Error: provide source_code or description to update"
        resp = requests.patch(f"{base}/tools/{tool_id}", headers=headers, json=payload)
        if resp.status_code == 200:
            return f"Updated: {tool_id}"
        return f"Update failed: {resp.status_code} {resp.text[:300]}"

    elif action == "attach":
        if not tool_id:
            return "Error: tool_id required for attach"
        # SAFE ATTACH: read current tools first, then append
        agent_resp = requests.get(f"{base}/agents/{agent_id}", headers=headers)
        if agent_resp.status_code != 200:
            return f"Could not read agent: {agent_resp.status_code}"
        current_tool_ids = [t["id"] for t in agent_resp.json().get("tools", [])]
        if tool_id in current_tool_ids:
            return f"Tool {tool_id} is already attached"
        current_tool_ids.append(tool_id)
        resp = requests.patch(f"{base}/agents/{agent_id}", headers=headers, json={"tool_ids": current_tool_ids})
        if resp.status_code == 200:
            return f"Attached {tool_id}"
        return f"Attach failed: {resp.status_code} {resp.text[:300]}"

    elif action == "detach":
        if not tool_id:
            return "Error: tool_id required for detach"
        # SAFE DETACH: read current tools, remove just this one
        agent_resp = requests.get(f"{base}/agents/{agent_id}", headers=headers)
        if agent_resp.status_code != 200:
            return f"Could not read agent: {agent_resp.status_code}"
        current_tool_ids = [t["id"] for t in agent_resp.json().get("tools", [])]
        if tool_id not in current_tool_ids:
            return f"Tool {tool_id} is not currently attached"
        current_tool_ids.remove(tool_id)
        resp = requests.patch(f"{base}/agents/{agent_id}", headers=headers, json={"tool_ids": current_tool_ids})
        if resp.status_code == 200:
            return f"Detached {tool_id} (data still on server — use attach to get it back)"
        return f"Detach failed: {resp.status_code} {resp.text[:300]}"

    elif action == "list":
        agent_resp = requests.get(f"{base}/agents/{agent_id}", headers=headers)
        if agent_resp.status_code != 200:
            return f"List failed: {agent_resp.status_code}"
        tools = agent_resp.json().get("tools", [])
        return json.dumps([{"id": t["id"], "name": t["name"], "desc": t.get("description", "")[:100]} for t in tools], indent=2)

    return f"Unknown action: {action}. Use create, update, attach, detach, or list."
