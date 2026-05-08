"""
Executor — carries out the action part of each step.
Returns {"success": bool, "output": str, "error": str}
"""
import os, subprocess

def execute(step) -> dict:
    atype  = step.action_type.lower()
    action = step.action

    try:
        if atype == "cmd":
            return _run_cmd(str(action), step.timeout)

        elif atype == "python":
            if callable(action):
                result = action()
                return {"success": True, "output": str(result or ""), "error": ""}
            else:
                exec(str(action), {})
                return {"success": True, "output": "Python executed.", "error": ""}

        elif atype == "file_create":
            # action = "path::content" or just "path"
            if "::" in str(action):
                path, content = str(action).split("::", 1)
            else:
                path, content = str(action), ""
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "output": f"Created: {path}", "error": ""}

        elif atype == "file_delete":
            path = str(action)
            if os.path.exists(path):
                os.remove(path)
                return {"success": True, "output": f"Deleted: {path}", "error": ""}
            return {"success": False, "output": "", "error": f"File not found: {path}"}

        elif atype == "noop":
            return {"success": True, "output": "No action (noop).", "error": ""}

        else:
            return {"success": False, "output": "", "error": f"Unknown action type: {atype}"}

    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def _run_cmd(command: str, timeout: int) -> dict:
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout + r.stderr).strip()
        return {"success": r.returncode == 0, "output": out, "error": "" if r.returncode == 0 else out}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}
