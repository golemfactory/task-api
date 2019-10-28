from typing import Any, Dict, List

from dataclasses import dataclass


@dataclass
class Subtask:
    params: dict
    resources: List[str]


@dataclass
class Task:
    env_id: str
    prerequisites: Dict[str, Any]
