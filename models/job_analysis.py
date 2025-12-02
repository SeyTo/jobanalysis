from dataclasses import dataclass
from typing import Optional


@dataclass
class ScoreResult:
    score: float
    gates_passed: bool
    fail_reason: Optional[str]
    matched_by_section: dict[str, dict[str, int]]
    bm25f: float


@dataclass
class JobDescpSection:
    weight: float
    headers: list[str]
