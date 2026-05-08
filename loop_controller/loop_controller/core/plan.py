"""
Plan dataclass — defines a goal, its steps, and how to verify success.

A step is a dict:
  {
    "name":    "human label",
    "type":    "cmd" | "file" | "output" | "app" | "python",
    "action":  str | callable,   # what to DO
    "check": {                   # how to VERIFY (mirrors checker rules)
        "type":   "file" | "output" | "cmd" | "app",
        "params": {...}
    }
  }
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Step:
    name:        str
    action_type: str          # "cmd" | "python" | "file_create" | "file_delete" | "noop"
    action:      object       # str (command) or callable
    check_type:  str          # checker rule type
    check_params: dict        # params passed to checker
    timeout:     int = 30     # seconds
    retryable:   bool = True

@dataclass
class Plan:
    goal:        str
    steps:       List[Step]   = field(default_factory=list)
    max_retries: int          = 3
    retry_delay: float        = 1.0   # seconds between retries
    description: str          = ""
