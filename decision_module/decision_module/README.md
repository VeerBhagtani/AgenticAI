# Decision Module

Routes a natural language goal to the correct agent — Web Agent or PC Agent.

## Run
```bash
python main.py "what is the latest iPhone price"   # → WEB_AGENT
python main.py "open notepad"                       # → PC_AGENT
python main.py "find best Python libraries and install them"  # → BOTH
python main.py                                      # interactive
```

## Decision Categories

| Category | When | Agent Used |
|---|---|---|
| `WEB_AGENT` | Goal needs information from the internet | Search + extract |
| `PC_AGENT` | Goal needs a local system action | Execute + verify |
| `BOTH` | Needs info first, then act locally | Web → PC in sequence |
| `UNKNOWN` | Cannot determine | Ask for clarification |

## Output Fields

| Field | Description |
|---|---|
| `category` | WEB_AGENT / PC_AGENT / BOTH / UNKNOWN |
| `agent` | Human-readable label |
| `confidence` | 0.0–1.0 |
| `web_score` | Raw info-seeking signal score |
| `pc_score` | Raw action signal score |
| `reasoning` | Why this decision was made |
| `suggested_steps` | Step-by-step plan |
| `suggested_params` | Params to pass to the agent |

## Confidence Logic
- Winning side score >> losing → high confidence  
- Scores close together → routes to BOTH  
- No signals at all → UNKNOWN

## Extending
- Add keyword signals in `core/classifier.py` → `WEB_SIGNALS` / `PC_SIGNALS`  
- Add PC action inference in `core/planner.py` → `_infer_pc_steps()`
