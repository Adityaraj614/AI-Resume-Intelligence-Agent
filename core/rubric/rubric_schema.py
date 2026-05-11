from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class RubricDimension:
    dimension_id: str
    dimension_name: str
    weight: float
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RubricScore:
    dimension_id: str
    dimension_name: str
    weight: float
    raw_score: float
    weighted_score: float
    explanation: str
    confidence: float
    source_fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RubricSummary:
    candidate_id: str
    candidate_name: str
    total_weighted_score: float
    max_weighted_score: float
    overall_percentage: float
    overall_label: str
    strongest_dimension: str
    weakest_dimension: str
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RubricBreakdown:
    candidate_id: str
    candidate_name: str
    scores: List[RubricScore]
    summary: RubricSummary
    source: str = "rubric_mapping"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "scores": [score.to_dict() for score in self.scores],
            "summary": self.summary.to_dict(),
            "source": self.source,
        }
