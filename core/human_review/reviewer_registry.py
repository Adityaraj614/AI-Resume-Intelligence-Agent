import hashlib
from typing import Any, Dict

from core.human_review.review_schema import ReviewerMetadata
from core.human_review.review_utils import clean_text, deterministic_serialize


def build_reviewer_id(reviewer_name: Any, source: str = "human_review") -> str:
    identity = {
        "reviewer_name": clean_text(reviewer_name).lower(),
        "source": clean_text(source).lower() or "human_review",
    }
    digest = hashlib.sha256(
        deterministic_serialize(identity).encode("utf-8")
    ).hexdigest()[:12]

    return f"reviewer_{digest}"


def normalize_reviewer_metadata(
    reviewer_name: Any,
    reviewer_id: Any = "",
    source: str = "human_review",
) -> ReviewerMetadata:
    normalized_name = clean_text(reviewer_name)

    if not normalized_name:
        raise ValueError("reviewer_name is required.")

    normalized_source = clean_text(source) or "human_review"
    normalized_id = clean_text(reviewer_id) or build_reviewer_id(
        normalized_name,
        normalized_source,
    )

    return ReviewerMetadata(
        reviewer_id=normalized_id,
        reviewer_name=normalized_name,
        source=normalized_source,
    )


def format_reviewer_metadata(reviewer: ReviewerMetadata) -> Dict[str, Any]:
    return reviewer.to_dict()
