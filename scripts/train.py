from __future__ import annotations

import os
from pathlib import Path

from data_layer.artifacts_repository import save_bundle
from data_layer.dataset_repository import load_csv
from logic_layer.modeling_service import fit_kmeans_k4


def _resolve_ref_data_path() -> str:
    """
    Résout le chemin du CSV d'entraînement.
    Priorité:
      1) REF_DATA_PATH (env)
      2) data/Mall_Customers.csv
    """
    env_path = os.getenv("REF_DATA_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists() and p.is_file():
            return str(p)
        raise FileNotFoundError(f"REF_DATA_PATH is set but invalid: {env_path}")

    default = Path("data") / "Mall_Customers.csv"
    if default.exists() and default.is_file():
        return str(default)

    raise FileNotFoundError(
        "Training CSV not found. Provide REF_DATA_PATH env var or add data/Mall_Customers.csv"
    )


def main() -> None:
    csv_path = _resolve_ref_data_path()
    df = load_csv(csv_path)
    bundle = fit_kmeans_k4(df, random_state=42)
    save_bundle(bundle)
    print("Artifacts generated in ./artifacts")


if __name__ == "__main__":
    main()
