from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import joblib


# Racine projet = parent de data_layer/
BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BASE_DIR / "artifacts"

PIPELINE_FILENAME = "clustering_pipeline.joblib"
METADATA_FILENAME = "metadata.json"


@dataclass(frozen=True)
class ModelBundle:
    pipeline: Any
    metadata: Dict[str, Any]

    @property
    def expected_columns(self):
        return self.metadata.get("expected_columns", [])

    @property
    def model_name(self):
        return self.metadata.get("model_name")

    @property
    def params(self):
        return self.metadata.get("params", {})

    @property
    def metrics(self):
        return self.metadata.get("metrics", {})
    

def save_bundle(bundle: ModelBundle) -> Dict[str, str]:
    """
    Sauvegarde:
    - pipeline: artifacts/clustering_pipeline.joblib
    - metadata: artifacts/metadata.json
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    pipeline_path = ARTIFACTS_DIR / PIPELINE_FILENAME
    metadata_path = ARTIFACTS_DIR / METADATA_FILENAME

    joblib.dump(bundle.pipeline, pipeline_path)
    metadata_path.write_text(json.dumps(bundle.metadata, indent=2), encoding="utf-8")

    return {"pipeline_path": str(pipeline_path), "metadata_path": str(metadata_path)}


def read_metadata() -> Dict[str, Any]:
    """
    Lit artifacts/metadata.json
    """
    metadata_path = ARTIFACTS_DIR / METADATA_FILENAME
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_bundle(artifacts_dir: Optional[str] = None) -> ModelBundle:
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
    return ModelBundle(pipeline=pipeline, metadata=metadata)
