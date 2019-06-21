from typing import List, NamedTuple


class Subtask(NamedTuple):
    subtask_id: str
    params: dict
    resources: List[str]
