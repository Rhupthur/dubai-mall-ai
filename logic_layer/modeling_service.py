from typing import Dict, Any
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline

from .domain import ClusteringBundle
from .preprocessing import EXPECTED_COLUMNS, split_feature_types, build_preprocessor, prepare_features
from .evaluation_service import clustering_metrics

def fit_kmeans_k4(df: pd.DataFrame, random_state: int = 42) -> ClusteringBundle:
    n_clusters = 4

    X_df = prepare_features(df, EXPECTED_COLUMNS)
    numeric_cols, categorical_cols = split_feature_types(EXPECTED_COLUMNS)
    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    pipe = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("model", model),
    ])

    pipe.fit(X_df)

    X = pipe.named_steps["preprocess"].transform(X_df)
    labels = pipe.named_steps["model"].labels_
    metrics = clustering_metrics(X, labels)

    params: Dict[str, Any] = {"n_clusters": n_clusters, "random_state": random_state, "n_init": 10}

    return ClusteringBundle(
        pipeline=pipe,
        expected_columns=EXPECTED_COLUMNS,
        model_name="kmeans",
        params=params,
        metrics=metrics,
    )
