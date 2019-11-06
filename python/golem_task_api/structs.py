from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field


@dataclass
class Infrastructure:
    min_memory_mib: Optional[float] = None


@dataclass
class Subtask:
    params: dict
    resources: List[str]


@dataclass
class Task:
    env_id: str
    prerequisites: Dict[str, Any]
    inf_requirements: Infrastructure = field(default_factory=Infrastructure)
