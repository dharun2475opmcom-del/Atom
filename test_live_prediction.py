
from src.virtual_sensors import VirtualSensorSimulator
from src.live_predictor import AquaGuardLivePredictor


# Initialize virtual sensors and trained AI model
simulator = VirtualSensorSimulator()
predictor = AquaGuardLivePredictor()


# ------------------------------------------
# TEST 1: AUTOMATIC SENSOR READING
# ------------------------------------------

print("\n========== AUTOMATIC SENSOR + MTNN TEST ==========")

reading = simulator.get_automatic_reading(
    filter_type="sediment",
    step=10
)

prediction = predictor.predict(reading)

print("\nSensor readings:")
print("Filter:", reading["filter_type"])
print("Pressure:", reading["pressure_diff"])
print("Flow:", reading["flow_rate"])
print("Turbidity:", reading["turbidity"])
print("Temperature:", reading["temperature"])

print("\nMTNN predictions:")
print("Fault:", prediction["fault"]["status"])
print("Fault confidence:", prediction["fault"]["confidence"])
print("RUL:", round(prediction["rul_days"], 2), "days")
print("Anomaly probability:", prediction["anomaly"]["probability"])


# ------------------------------------------
# TEST 2: SCENARIO-BASED SENSOR + MTNN TEST
# ------------------------------------------

print("\n========== SCENARIO + MTNN TEST ==========")

scenarios = [
    "Normal",
    "Degrading",
    "Clogged",
    "Anomaly",
    "Cleaning"
]

for scenario in scenarios:

    reading = simulator.get_scenario_reading(
        filter_type="sediment",
        scenario=scenario,
        cleaning_outcome="Successful"
    )

    prediction = predictor.predict(reading)

    print("\nScenario:", scenario)

    print("Pressure:", round(float(reading["pressure_diff"]), 2))
    print("Flow:", round(float(reading["flow_rate"]), 2))
    print("Turbidity:", round(float(reading["turbidity"]), 2))

    print("Predicted fault:", prediction["fault"]["status"])

    print(
        "Predicted RUL:",
        round(prediction["rul_days"], 2),
        "days"
    )

    print(
        "Anomaly probability:",
        round(prediction["anomaly"]["probability"] * 100, 2),
        "%"
    )

    if prediction["cleaning"] is not None:
        print(
            "Cleaning prediction:",
            prediction["cleaning"]["status"]
        )

print("\nAquaGuard sensor-to-MTNN connection test completed!")
