from core.workflow.workflow_metrics import (
    WorkflowTimer,
    build_empty_workflow_metrics,
    merge_workflow_metrics,
)


def test_workflow_timer_records_deterministic_duration_units():
    timer = WorkflowTimer()

    timer.record("ranking")
    timer.record("analytics")

    assert timer.build_metrics() == {
        "analytics_duration": 1,
        "duration_unit": "deterministic_step",
        "ranking_duration": 1,
        "total_workflow_duration": 2,
    }


def test_empty_workflow_metrics_are_stable():
    assert build_empty_workflow_metrics() == {
        "total_workflow_duration": 0,
        "duration_unit": "deterministic_step",
    }


def test_merge_workflow_metrics_combines_duration_fields():
    merged = merge_workflow_metrics(
        {"ranking_duration": 1, "total_workflow_duration": 1},
        {"export_duration": 1, "total_workflow_duration": 1},
    )

    assert merged["ranking_duration"] == 1
    assert merged["export_duration"] == 1
    assert merged["total_workflow_duration"] == 2
    assert merged["duration_unit"] == "deterministic_step"
