from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

EXPECTED_COLUMNS: List[str] = ["Gender", "Age", "Annual Income (k$)", "Spending Score (1-100)"]
DROP_COLUMNS: List[str] = ["CustomerID"]

PIPELINE_FILENAME = "clustering_pipeline.joblib"
METADATA_FILENAME = "metadata.json"
