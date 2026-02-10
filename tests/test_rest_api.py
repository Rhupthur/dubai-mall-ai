import io
import pandas as pd
from fastapi.testclient import TestClient

from main import app


def test_health():
    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


def test_cluster_row():
    payload = {
        "Gender": "Male",
        "Age": 30,
        "Annual Income (k$)": 60,
        "Spending Score (1-100)": 50,
    }

    with TestClient(app) as client:
        res = client.post("/api/cluster/row", json=payload)

        assert res.status_code == 200, res.text
        data = res.json()

        assert "cluster_id" in data
        assert isinstance(data["cluster_id"], int)


def test_cluster_file():
    df = pd.DataFrame(
        [
            {
                "Gender": "Male",
                "Age": 30,
                "Annual Income (k$)": 60,
                "Spending Score (1-100)": 50,
            },
            {
                "Gender": "Female",
                "Age": 22,
                "Annual Income (k$)": 40,
                "Spending Score (1-100)": 70,
            },
        ]
    )

    csv_bytes = io.BytesIO()
    df.to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)

    with TestClient(app) as client:
        res = client.post(
            "/api/cluster/file",
            files={"file": ("test.csv", csv_bytes, "text/csv")},
        )

        assert res.status_code == 200, res.text
        data = res.json()

        assert data["n_rows"] == 2
        assert "cluster_counts" in data
