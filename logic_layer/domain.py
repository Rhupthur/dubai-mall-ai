from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class ClusteringBundle:
    pipeline: Pipeline
    expected_columns: list[str]
    params: dict[str, Any]
    metrics: dict[str, float]
    model_name: str = "kmeans"

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "expected_columns": self.expected_columns,
            "params": self.params,
            "metrics": self.metrics,
        }


ModelBundle = ClusteringBundle

