from core.export.csv_exporter import (
    export_to_csv,
    flatten_record,
    normalize_csv_rows,
    resolve_csv_fieldnames,
)


EXPORT_OUTPUT_DIR = "tests/export_outputs"


def test_flatten_record_flattens_nested_structures():
    flattened = flatten_record({
        "candidate_id": "resume_001",
        "scores": {"final": 8.5},
        "risk_flags": ["LOW_CONFIDENCE", "LOW_EVIDENCE"],
    })

    assert flattened["candidate_id"] == "resume_001"
    assert flattened["scores.final"] == "8.5"
    assert flattened["risk_flags"] == "LOW_CONFIDENCE; LOW_EVIDENCE"


def test_normalize_csv_rows_extracts_candidate_decisions():
    rows = normalize_csv_rows({
        "candidate_decisions": [
            {"candidate_id": "resume_001", "interview_priority": "PRIORITY_INTERVIEW"}
        ]
    })

    assert rows == [
        {
            "candidate_id": "resume_001",
            "interview_priority": "PRIORITY_INTERVIEW",
        }
    ]


def test_resolve_csv_fieldnames_uses_preferred_then_sorted_fields():
    fieldnames = resolve_csv_fieldnames([
        {"candidate_name": "Asha", "z_field": "z", "candidate_id": "resume_001"}
    ])

    assert fieldnames == ["candidate_id", "candidate_name", "z_field"]


def test_export_to_csv_writes_header_and_rows():
    output_path = f"{EXPORT_OUTPUT_DIR}/shortlist.csv"
    rows = export_to_csv(
        [
            {
                "candidate_id": "resume_001",
                "candidate_name": "Asha Rao",
                "final_score": 8.9,
                "bucket": "STRONG_MATCH",
            }
        ],
        output_path,
    )
    with open(output_path, encoding="utf-8") as csv_file:
        content = csv_file.read()

    assert rows[0]["candidate_id"] == "resume_001"
    assert "candidate_id,candidate_name,final_score,bucket" in content
    assert "resume_001,Asha Rao,8.9,STRONG_MATCH" in content
