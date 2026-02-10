from typing import Any, Dict, List
import pandas as pd

from .domain import ClusteringBundle
from .preprocessing import prepare_features

def predict_one(bundle: ClusteringBundle, features: Dict[str, Any]) -> int:
    df = pd.DataFrame([features])
    X_df = prepare_features(df, bundle.expected_columns)
    cluster = bundle.pipeline.predict(X_df)[0]
    return int(cluster)

def predict_batch(bundle: ClusteringBundle, df: pd.DataFrame) -> List[int]:
    X_df = prepare_features(df, bundle.expected_columns)
    clusters = bundle.pipeline.predict(X_df)
    return [int(x) for x in clusters]
