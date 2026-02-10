from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd

from .domain import ClusteringBundle
from .preprocessing import prepare_features


@dataclass(frozen=True)
class ClusterProfile:
    cluster_id: int
    size: int
    pct: float
    mean_age: float
    mean_income: float
    mean_spending: float
    label: str


def _bucket(value: float, q_low: float, q_high: float) -> str:
    if value <= q_low:
        return "Low"
    if value >= q_high:
        return "High"
    return "Mid"


def _make_label(age_b: str, inc_b: str, spend_b: str) -> str:
    # Label lisible, orienté marketing
    parts = []
    parts.append(f"{inc_b} income")
    parts.append(f"{spend_b} spending")
    parts.append(f"{age_b} age")
    return " / ".join(parts)


def profile_clusters(
    bundle: ClusteringBundle,
    df_raw: pd.DataFrame,
    cluster_col: str = "cluster_id",
) -> Dict[str, Any]:
    """
    Retourne un résumé métier des segments :
    - counts / pourcentages
    - stats moyennes par cluster
    - labels heuristiques (Low/Mid/High) basés sur quantiles globaux
    """
    X_df = prepare_features(df_raw, bundle.expected_columns)

    clusters = bundle.pipeline.predict(X_df)
    df = X_df.copy()
    df[cluster_col] = clusters

    n = len(df)
    if n == 0:
        return {"n_rows": 0, "profiles": [], "warnings": ["Empty dataset"]}

    # Quantiles globaux pour catégoriser Low/Mid/High
    q_age_low, q_age_high = df["Age"].quantile([0.33, 0.66]).tolist()
    q_inc_low, q_inc_high = df["Annual Income (k$)"].quantile([0.33, 0.66]).tolist()
    q_sp_low, q_sp_high = df["Spending Score (1-100)"].quantile([0.33, 0.66]).tolist()

    grp = df.groupby(cluster_col, as_index=False).agg(
        size=("Age", "count"),
        mean_age=("Age", "mean"),
        mean_income=("Annual Income (k$)", "mean"),
        mean_spending=("Spending Score (1-100)", "mean"),
    )

    profiles: List[ClusterProfile] = []
    for _, row in grp.iterrows():
        cid = int(row[cluster_col])
        size = int(row["size"])
        pct = float(size / n)

        mean_age = float(row["mean_age"])
        mean_income = float(row["mean_income"])
        mean_spending = float(row["mean_spending"])

        age_b = _bucket(mean_age, q_age_low, q_age_high)
        inc_b = _bucket(mean_income, q_inc_low, q_inc_high)
        spend_b = _bucket(mean_spending, q_sp_low, q_sp_high)

        label = _make_label(age_b, inc_b, spend_b)

        profiles.append(
            ClusterProfile(
                cluster_id=cid,
                size=size,
                pct=pct,
                mean_age=mean_age,
                mean_income=mean_income,
                mean_spending=mean_spending,
                label=label,
            )
        )

    # Trier par taille décroissante (utile pour UI)
    profiles.sort(key=lambda p: p.size, reverse=True)

    return {
        "n_rows": n,
        "profiles": [p.__dict__ for p in profiles],
        "global_quantiles": {
            "age": {"q33": float(q_age_low), "q66": float(q_age_high)},
            "income": {"q33": float(q_inc_low), "q66": float(q_inc_high)},
            "spending": {"q33": float(q_sp_low), "q66": float(q_sp_high)},
        },
        "warnings": [],
    }
