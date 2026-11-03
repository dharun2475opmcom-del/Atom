
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

FILTERS = ["sediment", "carbon", "ro"]


def generate_dataset(number_of_purifiers=100, days=120):

    records = []

    for purifier in range(number_of_purifiers):

        for filter_type in FILTERS:

            failure_day = np.random.randint(80, 181)
            degradation = 0.0

            previous_pressure = 0.15
            previous_flow = 2.2

            if filter_type == "sediment":
                base_pressure = 0.15
                base_flow = 2.2
            elif filter_type == "carbon":
                base_pressure = 0.12
                base_flow = 2.0
            else:
                base_pressure = 0.10
                base_flow = 1.8

            for day in range(days):

                if day > 0:
                    degradation += 1.0 / failure_day
                    degradation += np.random.normal(0, 0.003)

                degradation = np.clip(degradation, 0, 1.1)

                # Sensor readings before cleaning
                pre_pressure = (
                    base_pressure + 0.70 * degradation
                    + np.random.normal(0, 0.025)
                )

                pre_flow = max(
                    0.1,
                    base_flow - 1.5 * degradation
                    + np.random.normal(0, 0.05)
                )

                cleaning_event = int(day == 50)
                cleaning_label = np.nan

                pressure = pre_pressure
                flow = pre_flow

                stored_pre_pressure = 0.0
                stored_post_pressure = 0.0
                stored_pre_flow = 0.0
                stored_post_flow = 0.0

                # Simulate cleaning
                if cleaning_event:

                    quality = np.random.choice(
                        ["failed", "partial", "successful"],
                        p=[0.15, 0.25, 0.60]
                    )

                    if quality == "successful":
                        recovery = np.random.uniform(0.75, 0.95)
                        cleaning_label = 2

                    elif quality == "partial":
                        recovery = np.random.uniform(0.35, 0.70)
                        cleaning_label = 1

                    else:
                        recovery = np.random.uniform(0.05, 0.25)
                        cleaning_label = 0

                    # Reduce degradation after cleaning
                    degradation *= (1 - recovery)

                    # Sensor readings after cleaning
                    post_pressure = (
                        base_pressure + 0.70 * degradation
                        + np.random.normal(0, 0.015)
                    )

                    post_flow = max(
                        0.1,
                        base_flow - 1.5 * degradation
                        + np.random.normal(0, 0.03)
                    )

                    stored_pre_pressure = pre_pressure
                    stored_post_pressure = post_pressure
                    stored_pre_flow = pre_flow
                    stored_post_flow = post_flow

                    pressure = post_pressure
                    flow = post_flow

                # Other sensor readings
                turbidity = max(
                    0.1,
                    1.0 + 1.5 * degradation
                    + np.random.normal(0, 0.15)
                )

                temperature = 25 + np.random.normal(0, 1.5)
                operating_hours = day * 8

                # Simulate abnormal pressure readings
                anomaly_label = int(np.random.random() < 0.04)

                if anomaly_label:
                    pressure += np.random.uniform(0.15, 0.30)

                pressure_trend = pressure - previous_pressure
                flow_trend = flow - previous_flow

                # Fault classification
                if degradation < 0.35:
                    fault_label = 0
                elif degradation < 0.70:
                    fault_label = 1
                else:
                    fault_label = 2

                # Remaining useful life
                rul_days = max(
                    0,
                    min(180, (1 - degradation) * failure_day)
                )

                record = {
                    "purifier_id": purifier,
                    "day": day,
                    "pressure_diff": pressure,
                    "flow_rate": flow,
                    "turbidity": turbidity,
                    "temperature": temperature,
                    "operating_hours": operating_hours,
                    "pressure_trend": pressure_trend,
                    "flow_trend": flow_trend,
                    "filter_type": filter_type,
                    "cleaning_event": cleaning_event,
                    "pre_pressure": stored_pre_pressure,
                    "post_pressure": stored_post_pressure,
                    "pre_flow": stored_pre_flow,
                    "post_flow": stored_post_flow,
                    "fault_label": fault_label,
                    "rul_days": rul_days,
                    "anomaly_label": anomaly_label,
                    "cleaning_label": cleaning_label
                }

                records.append(record)

                previous_pressure = pressure
                previous_flow = flow

    return pd.DataFrame(records)


if __name__ == "__main__":

    df = generate_dataset(
        number_of_purifiers=100,
        days=120
    )

    output = Path("data/raw")
    output.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output / "aquaguard_dataset.csv",
        index=False
    )

    print("Dataset generated successfully!")
    print("Dataset shape:", df.shape)
    print("Cleaning events:", df["cleaning_event"].sum())
    print("\nCleaning outcome distribution:")
    print(df["cleaning_label"].value_counts())
    print("\nFirst 5 rows:")
    print(df.head())
