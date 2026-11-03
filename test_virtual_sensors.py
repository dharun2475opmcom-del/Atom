
from src.virtual_sensors import VirtualSensorSimulator

simulator = VirtualSensorSimulator()

print("\n===== AUTOMATIC VIRTUAL SENSOR TEST =====")

for day in range(5):
    reading = simulator.get_automatic_reading(
        "sediment",
        day
    )

    print(f"\nSimulation reading {day + 1}")

    print("Pressure:", reading["pressure_diff"])
    print("Flow:", reading["flow_rate"])
    print("Turbidity:", reading["turbidity"])
    print("Temperature:", reading["temperature"])


print("\n===== SCENARIO SIMULATION TEST =====")

scenarios = [
    "Normal",
    "Degrading",
    "Clogged",
    "Anomaly",
    "Cleaning"
]

for scenario in scenarios:

    reading = simulator.get_scenario_reading(
        "sediment",
        scenario
    )

    print(f"\nScenario: {scenario}")

    print("Pressure:", reading["pressure_diff"])
    print("Flow:", reading["flow_rate"])
    print("Turbidity:", reading["turbidity"])
    print("Cleaning event:", reading["cleaning_event"])
