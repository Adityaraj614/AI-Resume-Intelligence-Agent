from typing import Any, Dict, List


DEFAULT_DURATION_UNITS = 1


class WorkflowTimer:
    """
    Deterministic workflow timer.

    The workflow layer reports elapsed work in stable duration units so repeated
    executions with identical module paths produce identical metrics.
    """

    def __init__(self, duration_units: int = DEFAULT_DURATION_UNITS) -> None:
        if duration_units < 0:
            raise ValueError("duration_units cannot be negative.")

        self.duration_units = duration_units
        self._metrics: Dict[str, int] = {}
        self._active_modules: List[str] = []

    def start(self, module_name: str) -> None:
        normalized_name = normalize_metric_name(module_name)
        if normalized_name not in self._active_modules:
            self._active_modules.append(normalized_name)

    def stop(self, module_name: str) -> int:
        normalized_name = normalize_metric_name(module_name)
        metric_name = f"{normalized_name}_duration"
        self._metrics[metric_name] = self._metrics.get(metric_name, 0) + self.duration_units

        if normalized_name in self._active_modules:
            self._active_modules.remove(normalized_name)

        return self._metrics[metric_name]

    def record(self, module_name: str) -> int:
        self.start(module_name)
        return self.stop(module_name)

    def build_metrics(self) -> Dict[str, Any]:
        total_duration = sum(
            value
            for key, value in self._metrics.items()
            if key.endswith("_duration")
        )

        return {
            **{
                key: self._metrics[key]
                for key in sorted(self._metrics)
            },
            "total_workflow_duration": total_duration,
            "duration_unit": "deterministic_step",
        }


def normalize_metric_name(module_name: str) -> str:
    normalized = str(module_name or "").strip().lower().replace(" ", "_")
    if not normalized:
        raise ValueError("module_name is required.")

    return normalized


def build_empty_workflow_metrics() -> Dict[str, Any]:
    return {
        "total_workflow_duration": 0,
        "duration_unit": "deterministic_step",
    }


def merge_workflow_metrics(*metric_sets: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "total_workflow_duration": 0,
        "duration_unit": "deterministic_step",
    }

    for metrics in metric_sets:
        if not isinstance(metrics, dict):
            continue

        for key, value in metrics.items():
            if key == "duration_unit":
                continue

            if key.endswith("_duration") or key == "total_workflow_duration":
                merged[key] = int(merged.get(key, 0)) + int(value or 0)
            else:
                merged[key] = value

    return {
        key: merged[key]
        for key in sorted(merged)
    }
