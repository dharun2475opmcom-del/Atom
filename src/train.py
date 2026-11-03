
import torch
import torch.nn as nn
import numpy as np

from torch.utils.data import TensorDataset, DataLoader
from pathlib import Path

from preprocessing import prepare_data
from model import AquaGuardMTNN


# Training configuration
EPOCHS = 30
BATCH_SIZE = 256
LEARNING_RATE = 0.001

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


def train_model():

    print("Loading preprocessed data...")

    train_data, test_data = prepare_data()

    # Convert training features into tensors
    X = torch.tensor(
        train_data["X"],
        dtype=torch.float32
    )

    y_fault = torch.tensor(
        train_data["fault"],
        dtype=torch.long
    )

    y_rul = torch.tensor(
        train_data["rul"],
        dtype=torch.float32
    )

    y_anomaly = torch.tensor(
        train_data["anomaly"],
        dtype=torch.float32
    )

    # Replace missing cleaning labels only in training tensors.
    # The mask ensures these replacement values are not trained.
    y_cleaning = torch.tensor(
        np.nan_to_num(
            train_data["cleaning"],
            nan=0.0
        ),
        dtype=torch.long
    )

    cleaning_mask = torch.tensor(
        train_data["cleaning_mask"],
        dtype=torch.bool
    )

    dataset = TensorDataset(
        X,
        y_fault,
        y_rul,
        y_anomaly,
        y_cleaning,
        cleaning_mask
    )

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    # Create model
    model = AquaGuardMTNN(
        input_size=15
    ).to(DEVICE)

    # Loss functions
    fault_loss_fn = nn.CrossEntropyLoss()

    rul_loss_fn = nn.MSELoss()

    # Handle imbalance in anomaly labels
    positive_count = float(y_anomaly.sum())
    negative_count = float(len(y_anomaly) - positive_count)

    pos_weight = torch.tensor(
        [negative_count / max(positive_count, 1)],
        dtype=torch.float32,
        device=DEVICE
    )

    anomaly_loss_fn = nn.BCEWithLogitsLoss(
        pos_weight=pos_weight
    )

    cleaning_loss_fn = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    print("\nStarting AquaGuard MTNN training...")
    print("Device:", DEVICE)
    print("Epochs:", EPOCHS)
    print("Batch size:", BATCH_SIZE)

    # Training loop
    for epoch in range(EPOCHS):

        model.train()

        total_epoch_loss = 0.0
        fault_epoch_loss = 0.0
        rul_epoch_loss = 0.0
        anomaly_epoch_loss = 0.0
        cleaning_epoch_loss = 0.0

        for batch in loader:

            (
                batch_X,
                batch_fault,
                batch_rul,
                batch_anomaly,
                batch_cleaning,
                batch_cleaning_mask
            ) = batch

            batch_X = batch_X.to(DEVICE)
            batch_fault = batch_fault.to(DEVICE)
            batch_rul = batch_rul.to(DEVICE)
            batch_anomaly = batch_anomaly.to(DEVICE)
            batch_cleaning = batch_cleaning.to(DEVICE)
            batch_cleaning_mask = batch_cleaning_mask.to(DEVICE)

            optimizer.zero_grad()

            predictions = model(batch_X)

            # Task 1: Fault diagnosis
            loss_fault = fault_loss_fn(
                predictions["fault"],
                batch_fault
            )

            # Task 2: Remaining useful life
            loss_rul = rul_loss_fn(
                predictions["rul"],
                batch_rul
            )

            # Task 3: Anomaly detection
            loss_anomaly = anomaly_loss_fn(
                predictions["anomaly"],
                batch_anomaly
            )

            # Task 4: Cleaning verification
            if batch_cleaning_mask.any():

                loss_cleaning = cleaning_loss_fn(
                    predictions["cleaning"][batch_cleaning_mask],
                    batch_cleaning[batch_cleaning_mask]
                )

            else:
                loss_cleaning = (
                    predictions["cleaning"].sum() * 0.0
                )

            # Combined multi-task loss
            total_loss = (
                loss_fault
                + loss_rul
                + loss_anomaly
                + loss_cleaning
            )

            total_loss.backward()

            # Prevent excessively large gradients
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0
            )

            optimizer.step()

            total_epoch_loss += total_loss.item()
            fault_epoch_loss += loss_fault.item()
            rul_epoch_loss += loss_rul.item()
            anomaly_epoch_loss += loss_anomaly.item()
            cleaning_epoch_loss += loss_cleaning.item()

        number_of_batches = len(loader)

        print(
            f"Epoch [{epoch + 1}/{EPOCHS}] "
            f"Total Loss: {total_epoch_loss / number_of_batches:.4f} | "
            f"Fault: {fault_epoch_loss / number_of_batches:.4f} | "
            f"RUL: {rul_epoch_loss / number_of_batches:.4f} | "
            f"Anomaly: {anomaly_epoch_loss / number_of_batches:.4f} | "
            f"Cleaning: {cleaning_epoch_loss / number_of_batches:.4f}"
        )

    # Save trained model
    Path("models").mkdir(
        parents=True,
        exist_ok=True
    )

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_size": 15
        },
        "models/aquaguard_mtnn.pth"
    )

    print("\nTraining completed successfully!")
    print("Model saved to models/aquaguard_mtnn.pth")


if __name__ == "__main__":
    train_model()
