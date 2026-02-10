from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClusteringBundle:
    pipeline: Any  # sklearn Pipeline: preprocess + model
    expected_columns: list[str]
    model_name: str
    params: dict[str, Any]
    metrics: dict[str, float]
    run_id: str | None = None  # pour MLflow plus tard
