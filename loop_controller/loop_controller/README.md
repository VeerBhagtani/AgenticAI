# Loop Controller

Goal-driven retry loop engine. Executes a plan step-by-step, checks each result, and retries with adjustments on failure.

## Run
```bash
python main.py demo           # all 3 demo plans
python main.py demo file      # file create/verify plan
python main.py demo cmd       # shell command plan
python main.py demo python    # python callable plan
python main.py                # interactive
```

## How It Works
```
for each step:
  attempt = 0
  while attempt <= max_retries:
      execute(step)
      check(step)
      if success → next step
      else → adjust(step, attempt) → retry
  if still failed → mark step failed
```

## Plan Structure
```python
from core.plan import Plan, Step

plan = Plan(
    goal        = "My goal description",
    max_retries = 3,
    retry_delay = 1.0,
    steps = [
        Step(
            name         = "Step label",
            action_type  = "cmd",          # cmd | python | file_create | file_delete | noop
            action       = "echo hello",   # string or callable
            check_type   = "output",       # file | app | output | cmd | noop
            check_params = {"expected": "hello", "source": "..."},
        ),
    ]
)

from core.controller import LoopController
result = LoopController().run(plan)
```

## Action Types
| Type | Action format | Description |
|---|---|---|
| `cmd` | shell string | Runs shell command |
| `python` | callable or code string | Runs Python |
| `file_create` | `"path::content"` | Creates file |
| `file_delete` | `"path"` | Deletes file |
| `noop` | `""` | No action (check only) |

## Check Types
| Type | Params | What it checks |
|---|---|---|
| `file` | `{"path": "..."}` | File/dir exists + size |
| `app` | `{"process": "..."}` | Process running |
| `output` | `{"expected": "...", "source": "file or string"}` | Text presence |
| `cmd` | `{"command": "...", "expected": "..."}` | Command output |
| `noop` | `{}` | Always passes |

## Retry Adjustments (auto-applied)
1. **Timeout error** → doubles step timeout
2. **2nd+ retry, cmd** → prepends `cmd /c` on Windows  
3. **3rd+ retry** → relaxes check threshold

## Logs
Saved to `logs/loop_YYYYMMDD_HHMMSS.log`
