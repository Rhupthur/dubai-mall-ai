from pathlib import Path

from data_layer.dataset_repository import load_csv
from data_layer.artifacts_repository import save_bundle
from logic_layer.modeling_service import fit_kmeans_k4

if __name__ == "__main__":
    # à adapter: chemin du CSV
    data_path = Path("data/Mall_Customers.csv")  # ou ton chemin réel
    df = load_csv(data_path)

    bundle = fit_kmeans_k4(df)
    print("Training metrics:", bundle.metrics)

    out = save_bundle(bundle)
    print("Saved:", out)
