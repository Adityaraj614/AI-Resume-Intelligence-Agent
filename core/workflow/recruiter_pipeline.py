from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from core.analytics.ranking_analytics import build_full_ranking_analytics
from core.analytics.ranking_stability import build_ranking_stability_report
from core.export.export_engine import build_export_artifact, export_report
from core.export.export_schema import DEFAULT_GENERATED_AT
from core.export.report_builder import build_recruiter_report
from core.recruiter.candidate_filter import filter_candidates
from core.recruiter.comparison_engine import compare_multiple_candidates
from core.recruiter.decision_support import generate_recruiter_decision_report
from core.recruiter.shortlist_engine import generate_shortlist
from core.workflow.workflow_metrics import WorkflowTimer
from core.workflow.workflow_schema import (
    normalize_workflow_result,
    validate_workflow_result,
)
from core.workflow.workflow_utils import (
    build_diagnostics,
    build_missing_candidate_warnings,
    build_workflow_metadata,
    build_workflow_summary,
    preserve_candidate_order,
)


MODULE_RANKING = "ranking"
MODULE_SHORTLIST = "shortlist"
MODULE_FILTERING = "filtering"
MODULE_COMPARISON = "comparison"
MODULE_ANALYTICS = "analytics"
MODULE_DECISION_SUPPORT = "decision_support"
MODULE_STABILITY = "stability"
MODULE_REPORT = "report"
MODULE_EXPORT = "export"

DEFAULT_MODULE_ORDER = (
    MODULE_RANKING,
    MODULE_SHORTLIST,
    MODULE_FILTERING,
    MODULE_COMPARISON,
    MODULE_ANALYTICS,
    MODULE_DECISION_SUPPORT,
    MODULE_STABILITY,
    MODULE_REPORT,
    MODULE_EXPORT,
)


@dataclass
class RecruiterPipelineDependencies:
    shortlist_builder: Callable[..., List[Dict[str, Any]]] = generate_shortlist
    candidate_filter: Callable[..., List[Dict[str, Any]]] = filter_candidates
    comparison_builder: Callable[[List[Dict[str, Any]]], Dict[str, Any]] = compare_multiple_candidates
    analytics_builder: Callable[[List[Dict[str, Any]]], Dict[str, Any]] = build_full_ranking_analytics
    decision_builder: Callable[..., Dict[str, Any]] = generate_recruiter_decision_report
    stability_builder: Callable[..., Dict[str, Any]] = build_ranking_stability_report
    report_builder: Callable[..., Dict[str, Any]] = build_recruiter_report
    export_writer: Callable[..., Dict[str, Any]] = export_report
    export_artifact_builder: Callable[..., Dict[str, Any]] = build_export_artifact


class RecruiterPipeline:
    """
    Central recruiter workflow coordinator.

    This class delegates all domain behavior to existing modules and only
    controls execution order, aggregation, diagnostics, and export handling.
    """

    def __init__(
        self,
        dependencies: Optional[RecruiterPipelineDependencies] = None,
    ) -> None:
        self.dependencies = dependencies or RecruiterPipelineDependencies()

    def run(
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
        if not isinstance(ranked_candidates, list):
            raise TypeError("ranked_candidates must be a list.")

        filters = recruiter_filters or {}
        timer = WorkflowTimer()
        modules_executed: List[str] = []
        completed_modules: List[str] = []
        failed_modules: Dict[str, str] = {}
        warnings: List[str] = []
        export_success = False

        ordered_candidates = preserve_candidate_order(ranked_candidates)
        shortlist: List[Dict[str, Any]] = []
        filtered_candidates: List[Dict[str, Any]] = []
        comparison_report: Dict[str, Any] = {}
        analytics_report: Dict[str, Any] = {}
        decision_support: Dict[str, Any] = {}
        stability_report: Dict[str, Any] = {}
        recruiter_report: Dict[str, Any] = {}
        export_metadata: Dict[str, Any] = {}

        self._record_success(
            MODULE_RANKING,
            modules_executed,
            completed_modules,
            timer,
        )

        shortlist = self._execute_module(
            MODULE_SHORTLIST,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.shortlist_builder,
            ordered_candidates,
            top_k=top_k,
            thresholds=thresholds,
            include_weak=include_weak,
            exclude_unsafe=exclude_unsafe,
        ) or []
        shortlist = self._merge_shortlist_with_ranked_candidates(
            shortlist,
            ordered_candidates,
        )

        filtered_candidates = self._execute_module(
            MODULE_FILTERING,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.candidate_filter,
            shortlist,
            **filters,
        ) or []
        warnings.extend(build_missing_candidate_warnings(shortlist, filtered_candidates))

        comparison_report = self._execute_module(
            MODULE_COMPARISON,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.comparison_builder,
            filtered_candidates,
        ) or {}

        analytics_report = self._execute_module(
            MODULE_ANALYTICS,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.analytics_builder,
            filtered_candidates,
        ) or {}

        decision_support = self._execute_module(
            MODULE_DECISION_SUPPORT,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.decision_builder,
            filtered_candidates,
            thresholds=thresholds,
        ) or {}

        stability_report = self._execute_module(
            MODULE_STABILITY,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.stability_builder,
            ordered_candidates,
            previous_rankings=previous_rankings,
        ) or {}

        recruiter_report = self._execute_module(
            MODULE_REPORT,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
            self.dependencies.report_builder,
            ranked_candidates=ordered_candidates,
            shortlist=shortlist,
            analytics_report=analytics_report,
            decision_report=decision_support,
            stability_report=stability_report,
        ) or {}

        export_result = self._execute_export(
            recruiter_report,
            export_format,
            export_path,
            execution_timestamp,
            modules_executed,
            completed_modules,
            failed_modules,
            timer,
        )
        export_metadata = export_result.get("export_metadata", {})
        export_success = export_result.get("export_success", False)

        priority_interview_count = len(decision_support.get("prioritized_interviews", []))
        diagnostics = build_diagnostics(
            modules_executed=modules_executed,
            completed_modules=completed_modules,
            failed_modules=failed_modules,
            warnings=warnings,
            export_success=export_success,
        )
        metadata = build_workflow_metadata(
            ordered_candidates,
            export_format=export_format,
            recruiter_filters=filters,
            execution_timestamp=execution_timestamp,
            completed_modules=completed_modules,
        )
        summary = build_workflow_summary(
            candidate_count=len(ordered_candidates),
            shortlist_count=len(shortlist),
            priority_interview_count=priority_interview_count,
            status=diagnostics["workflow_status"],
        )
        outputs = {
            "ranked_candidates": ordered_candidates,
            "shortlist": shortlist,
            "filtered_candidates": filtered_candidates,
            "comparison_report": comparison_report,
            "analytics_report": analytics_report,
            "decision_support": decision_support,
            "stability_report": stability_report,
            "recruiter_report": recruiter_report,
            "export_metadata": export_metadata,
        }
        result = normalize_workflow_result(
            workflow_metadata=metadata,
            workflow_summary=summary,
            workflow_outputs=outputs,
            workflow_metrics=timer.build_metrics(),
            diagnostics=diagnostics,
        )

        if not validate_workflow_result(result):
            raise ValueError("Workflow result failed schema validation.")

        return result

    def _record_success(
        self,
        module_name: str,
        modules_executed: List[str],
        completed_modules: List[str],
        timer: WorkflowTimer,
    ) -> None:
        modules_executed.append(module_name)
        timer.record(module_name)
        completed_modules.append(module_name)

    def _execute_module(
        self,
        module_name: str,
        modules_executed: List[str],
        completed_modules: List[str],
        failed_modules: Dict[str, str],
        timer: WorkflowTimer,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        modules_executed.append(module_name)
        timer.start(module_name)

        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            failed_modules[module_name] = str(exc)
            return None
        finally:
            timer.stop(module_name)

        completed_modules.append(module_name)
        return result

    def _execute_export(
        self,
        recruiter_report: Dict[str, Any],
        export_format: str,
        export_path: Optional[str],
        execution_timestamp: str,
        modules_executed: List[str],
        completed_modules: List[str],
        failed_modules: Dict[str, str],
        timer: WorkflowTimer,
    ) -> Dict[str, Any]:
        modules_executed.append(MODULE_EXPORT)
        timer.start(MODULE_EXPORT)

        try:
            if export_path:
                export_result = self.dependencies.export_writer(
                    data=recruiter_report,
                    output_path=export_path,
                    export_format=export_format,
                    report_type="recruiter_workflow",
                    generated_at=execution_timestamp,
                )
                metadata = {
                    "export_format": export_result.get("export_format", export_format),
                    "output_path": export_result.get("output_path", export_path),
                    "report_type": "recruiter_workflow",
                    "generated_at": execution_timestamp,
                }
            else:
                artifact = self.dependencies.export_artifact_builder(
                    data=recruiter_report,
                    report_type="recruiter_workflow",
                    generated_at=execution_timestamp,
                )
                metadata = {
                    **artifact.get("export_metadata", {}),
                    "export_format": str(export_format or "json").strip().lower(),
                    "output_path": "",
                }
        except Exception as exc:
            failed_modules[MODULE_EXPORT] = str(exc)
            return {
                "export_metadata": {},
                "export_success": False,
            }
        finally:
            timer.stop(MODULE_EXPORT)

        completed_modules.append(MODULE_EXPORT)
        return {
            "export_metadata": metadata,
            "export_success": True,
        }

    def _merge_shortlist_with_ranked_candidates(
        self,
        shortlist: List[Dict[str, Any]],
        ranked_candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        ranked_by_id = {
            str(candidate.get("candidate_id", "")): candidate
            for candidate in ranked_candidates
        }

        return [
            {
                **ranked_by_id.get(str(item.get("candidate_id", "")), {}),
                **item,
            }
            for item in shortlist
        ]
