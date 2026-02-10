import pytest
import pandas as pd

from data_layer.artifacts_repository import load_bundle
from logic_layer.prediction_service import predict_one, predict_batch


@pytest.fixture(scope="module")
def bundle():
    return load_bundle()


def test_predict_one_valid_returns_int(bundle):
    row = {
        "Gender": "Male",
        "Age": 30,
        "Annual Income (k$)": 60,
        "Spending Score (1-100)": 50,
    }

    cid = predict_one(bundle, row)

    assert isinstance(cid, int)
    assert cid >= 0


def test_predict_batch_valid_returns_list(bundle):
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

    cids = predict_batch(bundle, df)

    assert isinstance(cids, list)
    assert len(cids) == 2
    assert all(isinstance(x, int) for x in cids)
