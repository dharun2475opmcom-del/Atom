
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "pressure_diff",
    "flow_rate",
    "turbidity",
    "temperature",
    "operating_hours",
    "pressure_trend",
    "flow_trend",
    "cleaning_event",
    "pre_pressure",
    "post_pressure",
    "pre_flow",
    "post_flow",
    "filter_sediment",
    "filter_carbon",
    "filter_ro"
]

TARGETS = [
    "fault_label",
    "rul_days",
    "anomaly_label",
    "cleaning_label"
]


def prepare_data():

    # Load dataset
    df = pd.read_csv("data/raw/aquaguard_dataset.csv")

    print("Original dataset:", df.shape)

    # Encode filter type
    df = pd.get_dummies(
        df,
        columns=["filter_type"],
        dtype=int
    )

    # Ensure all filter columns exist
    for column in [
        "filter_type_sediment",
        "filter_type_carbon",
        "filter_type_ro"
    ]:
        if column not in df.columns:
            df[column] = 0

    # Rename encoded columns
    df = df.rename(columns={
        "filter_type_sediment": "filter_sediment",
        "filter_type_carbon": "filter_carbon",
        "filter_type_ro": "filter_ro"
    })

    # Prepare input and targets
    X = df[FEATURES].copy()

    y_fault = df["fault_label"].astype(int).to_numpy()
    y_rul = (
        df["rul_days"].to_numpy(dtype=np.float32) / 180.0
    )
    y_anomaly = df["anomaly_label"].astype(
        np.float32
    ).to_numpy()

    # Preserve NaN values for cleaning labels
    y_cleaning = df["cleaning_label"].to_numpy(
        dtype=np.float32
    )

    # Cleaning-event mask
    cleaning_mask = df["cleaning_event"].to_numpy(
        dtype=bool
    )

    # Split by purifier to prevent data leakage
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42
    )

    train_idx, test_idx = next(
        splitter.split(
            X,
            y_fault,
            groups=df["purifier_id"]
        )
    )

    X_train = X.iloc[train_idx].copy()
    X_test = X.iloc[test_idx].copy()

    # Scale using training data only
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Save scaler
    Path("models").mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        scaler,
        "models/preprocessing.pkl"
    )

    # Prepare output dictionary
    train_data = {
        "X": X_train,
        "fault": y_fault[train_idx],
        "rul": y_rul[train_idx],
        "anomaly": y_anomaly[train_idx],
        "cleaning": y_cleaning[train_idx],
        "cleaning_mask": cleaning_mask[train_idx]
    }

    test_data = {
        "X": X_test,
        "fault": y_fault[test_idx],
        "rul": y_rul[test_idx],
        "anomaly": y_anomaly[test_idx],
        "cleaning": y_cleaning[test_idx],
        "cleaning_mask": cleaning_mask[test_idx]
    }

    print("\nPreprocessing completed!")
    print("Training samples:", len(X_train))
    print("Testing samples:", len(X_test))
    print("Number of features:", X_train.shape[1])
    print(
        "Training cleaning events:",
        cleaning_mask[train_idx].sum()
    )
    print(
        "Testing cleaning events:",
        cleaning_mask[test_idx].sum()
    )

    return train_data, test_data


if __name__ == "__main__":
    prepare_data()
