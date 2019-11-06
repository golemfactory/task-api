from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field


@dataclass
class Infrastructure:
    @dataclass
    class Memory:
        gib: Optional[float] = None

    mem: Memory = field(default_factory=Memory)


@dataclass
class Subtask:
    params: dict
    resources: List[str]


@dataclass
class Task:
    env_id: str
    prerequisites: Dict[str, Any]
    inf_requirements: Infrastructure = field(default_factory=Infrastructure)
