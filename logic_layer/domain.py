from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class ClusteringBundle:
    pipeline: Any  # sklearn Pipeline: preprocess + model
    expected_columns: List[str]
    model_name: str
    params: Dict[str, Any]
    metrics: Dict[str, float]
    run_id: Optional[str] = None  # pour MLflow plus tard
