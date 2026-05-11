from typing import Any, Dict, List, Optional

from core.export.export_schema import DEFAULT_GENERATED_AT
from core.workflow.recruiter_pipeline import (
    RecruiterPipeline,
    RecruiterPipelineDependencies,
)


def run_recruiter_workflow(
    ranked_candidates: List[Dict[str, Any]],
    recruiter_filters: Optional[Dict[str, Any]] = None,
    export_format: str = "json",
    export_path: Optional[str] = None,
    previous_rankings: Optional[List[Dict[str, Any]]] = None,
    top_k: int = 10,
    include_weak: bool = False,
    exclude_unsafe: bool = True,
    thresholds: Optional[Dict[str, Dict[str, float]]] = None,
    execution_timestamp: str = DEFAULT_GENERATED_AT,
    dependencies: Optional[RecruiterPipelineDependencies] = None,
) -> Dict[str, Any]:
    """
    Run the complete recruiter workflow from ranked candidates to final export.
    """

    pipeline = RecruiterPipeline(dependencies=dependencies)
    return pipeline.run(
        ranked_candidates=ranked_candidates,
        recruiter_filters=recruiter_filters,
        export_format=export_format,
        export_path=export_path,
        previous_rankings=previous_rankings,
        top_k=top_k,
        include_weak=include_weak,
        exclude_unsafe=exclude_unsafe,
        thresholds=thresholds,
        execution_timestamp=execution_timestamp,
    )


class WorkflowManager:
    """
    Small facade for recruiter session orchestration.
    """

    def __init__(
        self,
        pipeline: Optional[RecruiterPipeline] = None,
    ) -> None:
        self.pipeline = pipeline or RecruiterPipeline()

    def run_recruiter_workflow(
        self,
        ranked_candidates: List[Dict[str, Any]],
        recruiter_filters: Optional[Dict[str, Any]] = None,
        export_format: str = "json",
        export_path: Optional[str] = None,
        previous_rankings: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 10,
        include_weak: bool = False,
        exclude_unsafe: bool = True,
        thresholds: Optional[Dict[str, Dict[str, float]]] = None,
        execution_timestamp: str = DEFAULT_GENERATED_AT,
    ) -> Dict[str, Any]:
        return self.pipeline.run(
            ranked_candidates=ranked_candidates,
            recruiter_filters=recruiter_filters,
            export_format=export_format,
            export_path=export_path,
            previous_rankings=previous_rankings,
            top_k=top_k,
            include_weak=include_weak,
            exclude_unsafe=exclude_unsafe,
            thresholds=thresholds,
            execution_timestamp=execution_timestamp,
        )
