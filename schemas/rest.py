from typing import Any, Dict, List, Optional
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
    cluster_label: Optional[str] = None
    cluster_pct: Optional[float] = None
    warnings: List[str] = []


class ClusterFileResponse(BaseModel):
    n_rows: int
    cluster_counts: Dict[str, int]
    profiles: List[ClusterProfile] = []
    preview: List[Dict[str, Any]]
    warnings: List[str] = []


class MetadataResponse(BaseModel):
    model_name: str
    expected_columns: List[str]
    params: Dict[str, Any]
    metrics: Dict[str, float]
