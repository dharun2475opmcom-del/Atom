
import torch
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
    mean_squared_error
)

from preprocessing import prepare_data
from model import AquaGuardMTNN


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


def evaluate_model():

    print("Loading testing data...")

    _, test_data = prepare_data()

    # Load trained model
    checkpoint = torch.load(
        "models/aquaguard_mtnn.pth",
        map_location=DEVICE,
        weights_only=True
    )

    model = AquaGuardMTNN(
        input_size=checkpoint["input_size"]
    ).to(DEVICE)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    X_test = torch.tensor(
        test_data["X"],
        dtype=torch.float32
    ).to(DEVICE)

    # Run predictions
    with torch.no_grad():

        predictions = model(X_test)

        fault_predictions = (
            torch.argmax(
                predictions["fault"],
                dim=1
            )
            .cpu()
            .numpy()
        )

        rul_predictions = (
            predictions["rul"]
            .cpu()
            .numpy() * 180.0
        )

        anomaly_predictions = (
            (torch.sigmoid(predictions["anomaly"]) >= 0.5)
            .int()
            .cpu()
            .numpy()
        )

        cleaning_predictions = (
            torch.argmax(
                predictions["cleaning"],
                dim=1
            )
            .cpu()
            .numpy()
        )

    print("\n========== AQUAGUARD EVALUATION ==========")

    # Task 1: Fault diagnosis
    print("\n1. FAULT DIAGNOSIS")

    print(
        "Accuracy:",
        round(
            accuracy_score(
                test_data["fault"],
                fault_predictions
            ),
            4
        )
    )

    print(
        classification_report(
            test_data["fault"],
            fault_predictions,
            labels=[0, 1, 2],
            target_names=[
                "Normal",
                "Degrading",
                "Clogged"
            ],
            zero_division=0
        )
    )

    # Task 2: Remaining useful life
    print("\n2. REMAINING USEFUL LIFE")

    rul_mae = mean_absolute_error(
        test_data["rul"] * 180.0,
        rul_predictions
    )

    rul_rmse = np.sqrt(
        mean_squared_error(
            test_data["rul"] * 180.0,
            rul_predictions
        )
    )

    print("MAE (days):", round(rul_mae, 2))
    print("RMSE (days):", round(rul_rmse, 2))

    # Task 3: Anomaly detection
    print("\n3. ANOMALY DETECTION")

    print(
        "Accuracy:",
        round(
            accuracy_score(
                test_data["anomaly"],
                anomaly_predictions
            ),
            4
        )
    )

    print(
        classification_report(
            test_data["anomaly"],
            anomaly_predictions,
            labels=[0, 1],
            target_names=[
                "Normal",
                "Anomaly"
            ],
            zero_division=0
        )
    )

    # Task 4: Cleaning verification
    print("\n4. CLEANING VERIFICATION")

    mask = test_data["cleaning_mask"]

    if mask.sum() > 0:

        actual_cleaning = (
            test_data["cleaning"][mask].astype(int)
        )

        predicted_cleaning = (
            cleaning_predictions[mask]
        )

        print(
            "Cleaning events tested:",
            int(mask.sum())
        )

        print(
            "Accuracy:",
            round(
                accuracy_score(
                    actual_cleaning,
                    predicted_cleaning
                ),
                4
            )
        )

        print(
            classification_report(
                actual_cleaning,
                predicted_cleaning,
                labels=[0, 1, 2],
                target_names=[
                    "Failed",
                    "Partial",
                    "Successful"
                ],
                zero_division=0
            )
        )

    else:
        print("No cleaning events in test data.")

    print("========== EVALUATION COMPLETE ==========")


if __name__ == "__main__":
    evaluate_model()
