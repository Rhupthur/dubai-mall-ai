from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

from data_layer.settings import ARTIFACTS_DIR, METADATA_FILENAME, PIPELINE_FILENAME
from logic_layer.domain import ModelBundle


def _extract_metadata(bundle: Any) -> dict[str, Any]:
    """
    Supporte:
    - ModelBundle (bundle.metadata existe)
    - ClusteringBundle (bundle.model_name / expected_columns / params / metrics)
    """
    meta = bundle.metadata if hasattr(bundle, "metadata") else None
    if isinstance(meta, dict):
        return meta

    return dict(meta)

    model_name = getattr(bundle, "model_name", "kmeans")
    expected_columns = getattr(bundle, "expected_columns", None)
    params = getattr(bundle, "params", {}) or {}
    metrics = getattr(bundle, "metrics", {}) or {}

    if expected_columns is None:
        # dernière sécurité si jamais c'est stocké ailleurs
        expected_columns = getattr(bundle, "EXPECTED_COLUMNS", [])

    return {
        "model_name": model_name,
        "expected_columns": list(expected_columns),
        "params": dict(params),
        "metrics": dict(metrics),
    }


def save_bundle(bundle: Any, artifacts_dir: str | None = None) -> None:
    """
    Sauvegarde pipeline + metadata dans artifacts/
    """
    base = Path(artifacts_dir) if artifacts_dir else ARTIFACTS_DIR
    base.mkdir(parents=True, exist_ok=True)

    pipeline_path = base / PIPELINE_FILENAME
    metadata_path = base / METADATA_FILENAME

    pipeline = getattr(bundle, "pipeline", None)
    if pipeline is None:
        raise ValueError("bundle.pipeline is missing (cannot save pipeline)")

    meta = _extract_metadata(bundle)

    joblib.dump(pipeline, pipeline_path)
    metadata_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def read_metadata(artifacts_dir: str | None = None) -> dict[str, Any]:
    """
    Lit metadata.json
    """
    base = Path(artifacts_dir) if artifacts_dir else ARTIFACTS_DIR
    metadata_path = base / METADATA_FILENAME
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_bundle(artifacts_dir: str | None = None) -> ModelBundle:
    """
    Charge pipeline + metadata depuis artifacts/
    """
    base = Path(artifacts_dir) if artifacts_dir else ARTIFACTS_DIR

    pipeline_path = base / PIPELINE_FILENAME
    metadata_path = base / METADATA_FILENAME

    if not pipeline_path.exists():
        raise FileNotFoundError(f"Pipeline not found: {pipeline_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    pipeline = joblib.load(pipeline_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    return ModelBundle(
        pipeline=pipeline,
        model_name=metadata.get("model_name", "kmeans"),
        expected_columns=metadata.get("expected_columns", []),
        params=metadata.get("params", {}),
        metrics=metadata.get("metrics", {}),
    )
