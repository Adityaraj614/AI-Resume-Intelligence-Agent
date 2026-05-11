import json

from core.export.json_exporter import (
    export_to_json,
    serialize_to_json,
)


EXPORT_OUTPUT_DIR = "tests/export_outputs"


def test_serialize_to_json_uses_deterministic_key_ordering():
    serialized = serialize_to_json({"b": 1, "a": 2})

    assert serialized.splitlines()[1].strip() == '"a": 2,'


def test_export_to_json_writes_payload():
    output_path = f"{EXPORT_OUTPUT_DIR}/report.json"
    payload = export_to_json(
        data=[{"candidate_id": "resume_001"}],
        output_path=output_path,
        report_type="ranked_candidates",
        report_summary="Ranking export contains 1 candidates.",
        generated_at="2026-01-01T00:00:00Z",
    )
    with open(output_path, encoding="utf-8") as json_file:
        written = json.load(json_file)

    assert written == payload
    assert written["export_metadata"]["report_type"] == "ranked_candidates"
