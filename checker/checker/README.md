# Task Checker

Local Python system for verifying if tasks are completed, with quality scoring.

## Setup
```bash
python main.py       # interactive
```
No dependencies beyond stdlib.

## Task Types

| Command | What it checks |
|---|---|
| `check file <path>` | File/dir exists + size/readability quality |
| `check app <process>` | Process running (tasklist / ps aux) |
| `check output <text> in <file_or_string>` | Expected text present (exact/partial/regex) |
| `check cmd <command> expects <text>` | Runs command, checks output |

## Output Fields
| Field | Description |
|---|---|
| `success` | True / False |
| `quality_score` | 0.0–1.0 (how good the result is) |
| `confidence` | 0.0–1.0 (how certain the verdict is) |
| `verdict` | HIGH QUALITY / ACCEPTABLE / LOW QUALITY / PARTIAL / FAILED |
| `recommendation` | What to do next |

## Examples
```
>> check file C:\output\report.txt
>> check app chrome.exe
>> check output Hello World in C:\test.txt
>> check cmd dir C:\ expects Users
```

## Adding New Rules
1. Create `rules/your_rule.py` with a `check(params) -> dict` function
2. Register it in `core/checker.py` RULE_MAP
```
