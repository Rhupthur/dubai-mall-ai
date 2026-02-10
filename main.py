from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data_layer.artifacts_repository import load_bundle
from data_layer.dataset_repository import load_csv
from logic_layer.explain_service import profile_clusters
from routers_layer.rest_router import router as api_router
from routers_layer.web_router import router as web_router

app = FastAPI(title="Dubai Mall Customer Segmentation")


def _resolve_ref_data_path() -> str:
    import os

    # 1) env var (doit être un FICHIER CSV)
    raw = os.environ.get("REF_DATA_PATH")
    if raw:
        p = Path(raw).expanduser()
        if p.is_file():
            return str(p)

    # 2) fallbacks (fichiers CSV existants)
    candidates = [
        Path("data/Mall_Customers.csv"),
        Path("data_layer/Mall_Customers.csv"),
        Path("data_layer/Mall_Customers.csv"),  # optionnel
    ]
    for p in candidates:
        if p.is_file():
            return str(p)

    # 3) erreur explicite (mieux qu’un crash pandas)
    raise FileNotFoundError(
        "Reference CSV not found. Set REF_DATA_PATH to a CSV file, "
        "or place Mall_Customers.csv in ./data/ or ./data_layer/"
    )


@app.on_event("startup")
def _startup() -> None:
    app.state.bundle = load_bundle()

    # Profils calculés une seule fois (dataset de référence)
    ref_path = _resolve_ref_data_path()
    df_ref = load_csv(ref_path)
    prof = profile_clusters(app.state.bundle, df_ref)

    # Map cluster_id -> profil
    app.state.cluster_profile_map = {p["cluster_id"]: p for p in prof["profiles"]}
    app.state.ref_n_rows = int(prof.get("n_rows", len(df_ref)))
    app.state.ref_data_path = ref_path


app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.include_router(web_router)                 # /
app.include_router(api_router, prefix="/api")  # /api/...
