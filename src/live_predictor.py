
import joblib
import pandas as pd
import torch

from pathlib import Path
from src.model import AquaGuardMTNN


# Exact feature order used during model training
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

FAULT_LABELS = {
    0: "Normal",
    1: "Degrading",
    2: "Clogged"
}

CLEANING_LABELS = {
    0: "Failed",
    1: "Partial",
    2: "Successful"
}


class AquaGuardLivePredictor:

    def __init__(self):

        # Project root directory
        self.base_dir = Path(__file__).resolve().parent.parent

        self.model_path = (
            self.base_dir / "models" / "aquaguard_mtnn.pth"
        )

        self.scaler_path = (
            self.base_dir / "models" / "preprocessing.pkl"
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # Check required files
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found: {self.model_path}"
            )

        if not self.scaler_path.exists():
            raise FileNotFoundError(
                f"Preprocessing scaler not found: {self.scaler_path}"
            )

        # Load saved preprocessing scaler
        self.scaler = joblib.load(self.scaler_path)

        # Load trained MTNN checkpoint
        checkpoint = torch.load(
            self.model_path,
            map_location=self.device,
            weights_only=True
        )

        input_size = checkpoint.get("input_size", len(FEATURES))

        if input_size != len(FEATURES):
            raise ValueError(
                f"Model expects {input_size} features, "
                f"but connector provides {len(FEATURES)}."
            )

        self.model = AquaGuardMTNN(input_size=input_size)

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model.to(self.device)
        self.model.eval()

        print("AquaGuard MTNN loaded successfully!")
        print("Device:", self.device)

    def prepare_features(self, reading):

        # Convert virtual sensor reading into model features
        filter_type = str(reading["filter_type"]).lower()

        if filter_type not in ["sediment", "carbon", "ro"]:
            raise ValueError(
                f"Invalid filter type: {filter_type}"
            )

        feature_values = {
            "pressure_diff": float(reading["pressure_diff"]),
            "flow_rate": float(reading["flow_rate"]),
            "turbidity": float(reading["turbidity"]),
            "temperature": float(reading["temperature"]),
            "operating_hours": float(reading["operating_hours"]),
            "pressure_trend": float(reading["pressure_trend"]),
            "flow_trend": float(reading["flow_trend"]),
            "cleaning_event": int(reading["cleaning_event"]),
            "pre_pressure": float(reading["pre_pressure"]),
            "post_pressure": float(reading["post_pressure"]),
            "pre_flow": float(reading["pre_flow"]),
            "post_flow": float(reading["post_flow"]),
            "filter_sediment": int(filter_type == "sediment"),
            "filter_carbon": int(filter_type == "carbon"),
            "filter_ro": int(filter_type == "ro")
        }

        # Preserve the exact training feature order
        input_df = pd.DataFrame(
            [[feature_values[name] for name in FEATURES]],
            columns=FEATURES
        )

        # Apply the already-fitted training scaler
        scaled_features = self.scaler.transform(input_df)

        return torch.tensor(
            scaled_features,
            dtype=torch.float32,
            device=self.device
        )

    def predict(self, reading):

        # Prepare sensor readings
        input_tensor = self.prepare_features(reading)

        # Run trained MTNN
        with torch.no_grad():

            outputs = self.model(input_tensor)

            # 1. Fault diagnosis
            fault_probabilities = torch.softmax(
                outputs["fault"], dim=1
            )[0]

            fault_class = int(
                torch.argmax(fault_probabilities).item()
            )

            # 2. Remaining useful life
            rul_normalized = float(
                outputs["rul"].item()
            )

            rul_days = rul_normalized * 180.0

            # 3. Anomaly detection
            anomaly_probability = float(
                torch.sigmoid(outputs["anomaly"]).item()
            )

            # 4. Cleaning verification
            cleaning_event = int(reading["cleaning_event"])

            if cleaning_event == 1:

                cleaning_probabilities = torch.softmax(
                    outputs["cleaning"], dim=1
                )[0]

                cleaning_class = int(
                    torch.argmax(cleaning_probabilities).item()
                )

                cleaning_result = {
                    "status": CLEANING_LABELS[cleaning_class],
                    "class": cleaning_class,
                    "probabilities": {
                        CLEANING_LABELS[i]: float(
                            cleaning_probabilities[i].item()
                        )
                        for i in range(3)
                    }
                }

            else:
                # Do not report a cleaning result when no
                # cleaning event has been recorded.
                cleaning_result = None

        return {
            "fault": {
                "status": FAULT_LABELS[fault_class],
                "class": fault_class,
                "confidence": float(
                    fault_probabilities[fault_class].item()
                ),
                "probabilities": {
                    FAULT_LABELS[i]: float(
                        fault_probabilities[i].item()
                    )
                    for i in range(3)
                }
            },

            "rul_days": max(0.0, rul_days),

            "anomaly": {
                "detected": anomaly_probability >= 0.5,
                "probability": anomaly_probability
            },

            "cleaning": cleaning_result
        }
