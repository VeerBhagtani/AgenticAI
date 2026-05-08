"""
Example plans ready to use or extend.
"""
import os
from core.plan import Plan, Step

TEMP = os.path.join(os.path.expanduser("~"), "loop_test")

def plan_create_file() -> Plan:
    """Create a temp file and verify it exists with content."""
    path = os.path.join(TEMP, "output.txt")
    return Plan(
        goal        = "Create a text file with content and verify it",
        description = "Creates output.txt then checks it exists with data",
        max_retries = 3,
        retry_delay = 0.5,
        steps = [
            Step(
                name         = "Create output directory",
                action_type  = "cmd",
                action       = f"mkdir \"{TEMP}\"" if os.name == "nt" else f"mkdir -p \"{TEMP}\"",
                check_type   = "file",
                check_params = {"path": TEMP},
            ),
            Step(
                name         = "Write file",
                action_type  = "file_create",
                action       = f"{path}::Hello from Loop Controller! Task complete.",
                check_type   = "file",
                check_params = {"path": path},
            ),
            Step(
                name         = "Verify content",
                action_type  = "noop",
                action       = "",
                check_type   = "output",
                check_params = {"expected": "Hello from Loop Controller", "source": path},
            ),
        ]
    )

def plan_run_and_verify() -> Plan:
    """Run a shell command and verify output."""
    return Plan(
        goal        = "Run echo command and verify output",
        max_retries = 2,
        retry_delay = 0.5,
        steps = [
            Step(
                name         = "Echo test message",
                action_type  = "cmd",
                action       = "echo Loop Controller Test Passed",
                check_type   = "cmd",
                check_params = {"command": "echo Loop Controller Test Passed", "expected": "Loop Controller"},
            ),
        ]
    )

def plan_python_task() -> Plan:
    """Run a Python callable and verify a file it creates."""
    out_path = os.path.join(TEMP, "python_out.txt")

    def write_file():
        os.makedirs(TEMP, exist_ok=True)
        with open(out_path, "w") as f:
            f.write("Python task completed successfully.")
        return f"Wrote to {out_path}"

    return Plan(
        goal        = "Execute Python function and verify output file",
        max_retries = 2,
        retry_delay = 0.3,
        steps = [
            Step(
                name         = "Run Python writer",
                action_type  = "python",
                action       = write_file,
                check_type   = "output",
                check_params = {"expected": "Python task completed", "source": out_path},
            ),
        ]
    )
