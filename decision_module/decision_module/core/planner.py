"""
Planner — given a classified goal, generates a suggested execution plan.
Not executing anything here — just describing what SHOULD happen.
"""

def suggest_plan(goal: str, category: str) -> dict:
    goal_lower = goal.lower()

    if category == "WEB_AGENT":
        return {
            "agent":  "WEB_AGENT",
            "steps": [
                f"1. Search DuckDuckGo/Google for: \"{goal}\"",
                "2. Fetch top result pages",
                "3. Extract and evaluate relevant content",
                "4. Return summarised answer with source URL",
            ],
            "params": {"query": goal}
        }

    elif category == "PC_AGENT":
        steps, params = _infer_pc_steps(goal_lower, goal)
        return {"agent": "PC_AGENT", "steps": steps, "params": params}

    elif category == "BOTH":
        return {
            "agent": "BOTH",
            "steps": [
                f"1. [WEB_AGENT] Search for information related to: \"{goal}\"",
                "2. [WEB_AGENT] Extract and summarise findings",
                "3. [PC_AGENT]  Use retrieved info to perform local action",
                "4. [CHECKER]   Verify the result",
            ],
            "params": {"query": goal}
        }

    else:
        return {
            "agent": "UNKNOWN",
            "steps": ["Clarify the goal — is this an info request or a local action?"],
            "params": {}
        }


def _infer_pc_steps(low: str, original: str):
    """Infer likely PC steps from keywords."""
    import re

    # Open app
    m = re.search(r"\b(open|launch|start)\b\s+(\w+)", low)
    if m:
        app = m.group(2)
        return (
            [f"1. Launch application: {app}", "2. Verify process is running"],
            {"action": "open_app", "target": app}
        )

    # Create file
    m = re.search(r"\b(create|make|write)\b.+\b(file|document|txt|csv)\b", low)
    if m:
        return (
            ["1. Create the specified file", "2. Write content if provided", "3. Verify file exists"],
            {"action": "create_file"}
        )

    # Delete file
    m = re.search(r"\b(delete|remove)\b.+\b(file|folder|directory)\b", low)
    if m:
        return (
            ["1. Locate the file/folder", "2. Delete it", "3. Verify deletion"],
            {"action": "delete_file"}
        )

    # Run command
    m = re.search(r"\b(run|execute|cmd)\b\s+(.+)", low)
    if m:
        cmd = m.group(2)
        return (
            [f"1. Execute command: {cmd}", "2. Capture output", "3. Verify exit code"],
            {"action": "run_cmd", "command": cmd}
        )

    # Shutdown / restart
    if re.search(r"\b(shutdown|restart|reboot)\b", low):
        return (
            ["1. Confirm with user (risky action)", "2. Execute shutdown/restart command"],
            {"action": "run_cmd", "command": "shutdown /r /t 0" if "restart" in low else "shutdown /s /t 0"}
        )

    # Generic fallback
    return (
        [f"1. Parse and execute: \"{original}\"", "2. Verify result"],
        {"action": "run_cmd", "command": original}
    )
