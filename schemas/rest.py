from typing import Any

from pydantic import BaseModel, Field


class ClusterProfile(BaseModel):
    cluster_id: int
    size: int
    pct: float
    mean_age: float
    mean_income: float
    mean_spending: float
    label: str


class ClusterRowRequest(BaseModel):
    Gender: str = Field(..., examples=["Male", "Female"])
    Age: float
    Annual_Income_k: float = Field(..., alias="Annual Income (k$)")
    Spending_Score: float = Field(..., alias="Spending Score (1-100)")

    class Config:
        populate_by_name = True


class ClusterRowResponse(BaseModel):
    cluster_id: int
    cluster_label: str | None = None
    cluster_pct: float | None = None
    warnings: list[str] = []


class ClusterFileResponse(BaseModel):
    n_rows: int
    cluster_counts: dict[str, int]
    profiles: list[ClusterProfile] = []
    preview: list[dict[str, Any]]
    warnings: list[str] = []


class MetadataResponse(BaseModel):
    model_name: str
    expected_columns: list[str]
    params: dict[str, Any]
    metrics: dict[str, float]
