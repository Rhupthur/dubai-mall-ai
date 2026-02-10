from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from data_layer.artifacts_repository import read_metadata
from logic_layer.explain_service import profile_clusters
from logic_layer.prediction_service import predict_batch, predict_one
from schemas.rest import (
    ClusterFileResponse,
    ClusterRowRequest,
    ClusterRowResponse,
    MetadataResponse,
)

router = APIRouter()


def _get_bundle(request: Request):
    bundle = getattr(request.app.state, "bundle", None)
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model bundle not loaded.")
    return bundle


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metadata", response_model=MetadataResponse)
def metadata() -> Any:
    return read_metadata()


@router.get("/profiles")
def get_profiles(request: Request) -> dict[str, Any]:
    prof_map = getattr(request.app.state, "cluster_profile_map", {})
    profiles = list(prof_map.values())
    return {"profiles": profiles}


@router.post("/cluster/row", response_model=ClusterRowResponse)
def cluster_row(request: Request, payload: ClusterRowRequest) -> ClusterRowResponse:
    bundle = _get_bundle(request)

    features = {
        "Gender": payload.Gender,
        "Age": payload.Age,
        "Annual Income (k$)": payload.Annual_Income_k,
        "Spending Score (1-100)": payload.Spending_Score,
    }

    try:
        cid = int(predict_one(bundle, features))
        prof_map = getattr(request.app.state, "cluster_profile_map", {})
        prof = prof_map.get(cid)

        label = prof.get("label") if prof else None
        pct = prof.get("pct") if prof else None

        return ClusterRowResponse(
            cluster_id=cid,
            cluster_label=label,
            cluster_pct=pct,
            warnings=[],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/cluster/file", response_model=ClusterFileResponse)
async def cluster_file(request: Request, file: UploadFile = File(...)) -> ClusterFileResponse:
    bundle = _get_bundle(request)

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        df_raw = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV read error: {e}") from e

    # Optionnel: drop CustomerID si présent
    if "CustomerID" in df_raw.columns:
        df_raw = df_raw.drop(columns=["CustomerID"])

    # Prédiction batch
    clusters = predict_batch(bundle, df_raw)
    df_out = df_raw.copy()
    df_out["cluster_id"] = clusters

    # Counts
    cluster_counts = df_out["cluster_id"].value_counts().sort_index()
    cluster_counts_dict = {str(int(k)): int(v) for k, v in cluster_counts.items()}

    # Preview (20 lignes)
    preview = df_out.head(20).to_dict(orient="records")

    # Profils (sur ce batch)
    prof = profile_clusters(bundle, df_raw)
    profiles = prof["profiles"]

    return ClusterFileResponse(
        n_rows=int(df_out.shape[0]),
        cluster_counts=cluster_counts_dict,
        profiles=profiles,
        preview=preview,
        warnings=[],
    )


@router.post("/cluster/file/export")
async def cluster_file_export(request: Request, file: UploadFile = File(...)):
    bundle = _get_bundle(request)

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        df_raw = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV read error: {e}") from e

    if "CustomerID" in df_raw.columns:
        df_raw = df_raw.drop(columns=["CustomerID"])

    clusters = predict_batch(bundle, df_raw)
    df_out = df_raw.copy()
    df_out["cluster_id"] = clusters

    bio = BytesIO()
    df_out.to_csv(bio, index=False)
    bio.seek(0)

    filename = file.filename.rsplit(".", 1)[0] + "_clustered.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(bio, media_type="text/csv", headers=headers)
