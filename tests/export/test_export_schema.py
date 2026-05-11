from core.export.export_schema import (
    infer_candidate_count,
    normalize_export_payload,
    validate_export_payload,
)


def test_normalize_export_payload_builds_stable_schema():
    payload = normalize_export_payload(
        report_type="decision_support",
        report_data={"candidate_count": 2},
        report_summary="Decision report.",
        generated_at="2026-01-01T00:00:00Z",
    )

    assert payload["export_metadata"]["report_type"] == "decision_support"
    assert payload["export_metadata"]["generated_at"] == "2026-01-01T00:00:00Z"
    assert payload["report_summary"] == "Decision report."


def test_validate_export_payload_accepts_complete_payload():
    payload = normalize_export_payload("analytics", {}, "Analytics report.")

    assert validate_export_payload(payload) is True


def test_validate_export_payload_rejects_missing_metadata():
    assert validate_export_payload({"report_data": {}}) is False


def test_infer_candidate_count_supports_common_report_shapes():
    assert infer_candidate_count([{"candidate_id": "a"}]) == 1
    assert infer_candidate_count({"candidate_count": 3}) == 3
    assert infer_candidate_count({"filtered_candidates": [{}, {}]}) == 2
    assert infer_candidate_count("not candidates") == 0

