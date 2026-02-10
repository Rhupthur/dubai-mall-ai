
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

EXPECTED_COLUMNS = ["Gender", "Age", "Annual Income (k$)", "Spending Score (1-100)"]

def validate_input_df(df: pd.DataFrame, expected_columns: list[str] = EXPECTED_COLUMNS) -> None:
    missing = [c for c in expected_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def split_feature_types(expected_columns: list[str] = EXPECTED_COLUMNS) -> tuple[list[str], list[str]]:
    categorical = ["Gender"]
    numeric = [c for c in expected_columns if c not in categorical]
    return numeric, categorical

def build_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> ColumnTransformer:
    numeric_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(drop="if_binary", handle_unknown="ignore")),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ],
        remainder="drop",
    )

def prepare_features(df: pd.DataFrame, expected_columns: list[str] = EXPECTED_COLUMNS) -> pd.DataFrame:
    validate_input_df(df, expected_columns)
    return df[expected_columns].copy()
