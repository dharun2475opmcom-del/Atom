
import pandas as pd
import numpy as np
from pathlib import Path


class VirtualSensorSimulator:

    def __init__(self, dataset_path=None):
        base_dir = Path(__file__).resolve().parent.parent

        if dataset_path is None:
            raw_dir = base_dir / "data" / "raw"

            if not raw_dir.exists():
                raise FileNotFoundError(
                    f"Dataset folder not found: {raw_dir}"
                )

            csv_files = list(raw_dir.glob("*.csv"))

            if not csv_files:
                raise FileNotFoundError(
                    "No CSV dataset found inside data/raw."
                )

            dataset_path = csv_files[0]

        self.df = pd.read_csv(dataset_path)

        required = [
            "purifier_id", "filter_type", "day",
            "pressure_diff", "flow_rate", "turbidity",
            "temperature", "operating_hours",
            "pressure_trend", "flow_trend",
            "cleaning_event", "pre_pressure",
            "post_pressure", "pre_flow", "post_flow"
        ]

        missing = [column for column in required
                   if column not in self.df.columns]

        if missing:
            raise ValueError(
                f"Dataset is missing columns: {missing}"
            )

        self.df = self.df.sort_values(
            ["purifier_id", "filter_type", "day"]
        ).reset_index(drop=True)

        self.streams = {}

        for filter_name in ["sediment", "carbon", "ro"]:
            rows = self.df[
                self.df["filter_type"] == filter_name
            ].copy()

            if rows.empty:
                raise ValueError(
                    f"No data found for filter: {filter_name}"
                )

            purifier = rows["purifier_id"].iloc[0]

            self.streams[filter_name] = (
                rows[rows["purifier_id"] == purifier]
                .sort_values("day")
                .reset_index(drop=True)
            )

        self.rng = np.random.default_rng()

    def get_automatic_reading(self, filter_type, step):

        rows = self.streams[filter_type]

        # Cycle through the simulated purifier readings.
        index = step % len(rows)

        reading = rows.iloc[index].copy()

        # The dataset supplies the sensor behaviour over time.
        return reading

    def get_scenario_reading(
        self,
        filter_type,
        scenario,
        cleaning_outcome="Successful"
    ):

        rows = self.streams[filter_type]

        # Use a middle-life reading as the reference condition.
        reading = rows.iloc[len(rows) // 2].copy()

        # Use the dataset's own ranges to scale simulated changes.
        pressure_std = max(
            float(self.df[
                self.df["filter_type"] == filter_type
            ]["pressure_diff"].std()),
            0.01
        )

        flow_std = max(
            float(self.df[
                self.df["filter_type"] == filter_type
            ]["flow_rate"].std()),
            0.01
        )

        turbidity_std = max(
            float(self.df[
                self.df["filter_type"] == filter_type
            ]["turbidity"].std()),
            0.01
        )

        reading["cleaning_event"] = 0

        if scenario == "Normal":
            pass

        elif scenario == "Degrading":
            reading["pressure_diff"] += 0.7 * pressure_std
            reading["flow_rate"] -= 0.7 * flow_std
            reading["turbidity"] += 0.3 * turbidity_std

        elif scenario == "Clogged":
            reading["pressure_diff"] += 1.5 * pressure_std
            reading["flow_rate"] -= 1.5 * flow_std
            reading["turbidity"] += 1.0 * turbidity_std

        elif scenario == "Anomaly":
            # Simulate an unusual sudden pressure spike.
            reading["pressure_diff"] += 3.0 * pressure_std
            reading["flow_rate"] = max(
                0,
                reading["flow_rate"] - 2.0 * flow_std
            )
            reading["turbidity"] += 2.0 * turbidity_std

        elif scenario == "Cleaning":
            reading["cleaning_event"] = 1

            before_pressure = (
                float(reading["pressure_diff"]) + pressure_std
            )

            before_flow = max(
                0,
                float(reading["flow_rate"]) - flow_std
            )

            recovery = {
                "Failed": 0.15,
                "Partial": 0.50,
                "Successful": 0.85
            }[cleaning_outcome]

            after_pressure = (
                before_pressure -
                recovery * pressure_std
            )

            after_flow = (
                before_flow +
                recovery * flow_std
            )

            reading["pre_pressure"] = before_pressure
            reading["post_pressure"] = after_pressure

            reading["pre_flow"] = before_flow
            reading["post_flow"] = after_flow

            reading["pressure_diff"] = after_pressure
            reading["flow_rate"] = after_flow

        else:
            raise ValueError(
                f"Unknown scenario: {scenario}"
            )

        # Avoid physically impossible negative readings.
        reading["pressure_diff"] = max(
            0, float(reading["pressure_diff"])
        )

        reading["flow_rate"] = max(
            0, float(reading["flow_rate"])
        )

        reading["turbidity"] = max(
            0, float(reading["turbidity"])
        )

        # Recalculate simple trends for the simulated reading.
        reading["pressure_trend"] = (
            float(reading["pressure_diff"]) -
            float(reading["pre_pressure"])
        )

        reading["flow_trend"] = (
            float(reading["flow_rate"]) -
            float(reading["pre_flow"])
        )

        return reading
