import logging
import random
from datetime import datetime


logger = logging.getLogger(__name__)


# Controls how often an abnormal event occurs.
# 0.05 = approximately 5% chance per generated reading.
ANOMALY_PROBABILITY = 0.05


# Normal machine baseline values
BASELINE = {
    "temperature": 72.0,
    "humidity": 50.0,
    "pressure": 101.3,
    "vibration": 0.30,
    "rpm": 1800.0,
    "battery": 90.0,
}


def generate_telemetry(device_id="MACHINE_01"):
    """
    Generate one synthetic telemetry reading.
    """

    from backend.services.demo_controller import get_scenario, get_telemetry_overrides

    scenario = get_scenario()

    # Small natural variation around baseline
    temperature = BASELINE["temperature"] + random.uniform(-3, 3)
    humidity = BASELINE["humidity"] + random.uniform(-4, 4)
    pressure = BASELINE["pressure"] + random.uniform(-1, 1)
    vibration = BASELINE["vibration"] + random.uniform(-0.08, 0.08)
    rpm = BASELINE["rpm"] + random.uniform(-100, 100)
    battery = BASELINE["battery"] - random.uniform(0, 0.2)

    # Decide whether this reading is abnormal
    is_anomaly = random.random() < ANOMALY_PROBABILITY

    if is_anomaly:

        temperature = random.uniform(90, 100)
        vibration = random.uniform(0.8, 1.2)
        rpm = random.uniform(2200, 2500)

        logger.warning(
            "Anomaly generated for %s",
            device_id
        )

    if scenario in ("AI01_MACHINE_INCIDENT", "RECOVERY"):
        demo = get_telemetry_overrides()
        temperature = demo["temperature"]
        humidity = demo["humidity"]
        pressure = demo["pressure"] / 10
        vibration = demo["vibration"]
        rpm = demo["rpm"]
        battery = demo["battery"]

    return {
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "pressure": round(pressure, 2),
        "vibration": round(vibration, 2),
        "rpm": round(rpm, 2),
        "battery": round(max(battery, 20), 2),
    }