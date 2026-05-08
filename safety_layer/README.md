# Safety Layer

Pre-execution risk scanner for commands. Auto-allows safe commands, prompts on risky ones, blocks critical ones without strong confirmation.

## Run
```bash
python main.py demo              # see all risk levels in action
python main.py "echo hello"      # auto-allowed
python main.py "shutdown /s"     # prompts for confirmation
python main.py                   # interactive
```

## Risk Levels

| Level | Color | Examples | Confirmation |
|---|---|---|---|
| `SAFE` | 🟢 | `echo`, `dir`, `ipconfig`, `open app` | Auto-allowed |
| `MEDIUM` | 🟡 | `rmdir`, `del file.txt`, `schtasks` | `yes` or `y` |
| `HIGH` | 🟠 | `shutdown`, `restart`, `taskkill`, wildcard `del *` | `yes` only |
| `CRITICAL` | 🔴 | `format c:`, `rm -rf /`, `reg delete`, `bcdedit` | Exact phrase required |

Critical confirmation phrase: `I understand the risk and confirm`

## Use From Other Agents
```python
from safety_gate import SafetyGate
gate = SafetyGate()

# Interactive (prompts user)
result = gate.check("shutdown /s /t 0")

# Programmatic (pre-supply answer)
result = gate.check("del report.txt", user_input="yes")

if result["approved"]:
    execute(result["command"])

# result fields:
#   approved  bool
#   level     SAFE | MEDIUM | HIGH | CRITICAL
#   action    ALLOW | DENY
#   reason    str
#   auto      bool  (True = no human needed)
```

## Batch Check
```python
commands = ["echo hi", "del *.log", "shutdown /s"]
results  = gate.check_all(commands, auto_confirm_medium=True)
```

## Extending Rules
Add to `core/rules.py`:
```python
RiskRule(
    pattern     = r"\byour_pattern\b",
    level       = "HIGH",
    description = "What this does and why it's dangerous.",
    examples    = ["example command"],
)
```
Add safe patterns to `SAFE_PATTERNS` list.
