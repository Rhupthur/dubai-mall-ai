from __future__ import annotations

from pathlib import Path
import pandas as pd

from .settings import DROP_COLUMNS

def load_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # drop colonnes inutiles si présentes
    for col in DROP_COLUMNS:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df
