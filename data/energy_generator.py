import random
from datetime import datetime, timezone
from backend.utils.config import get_demo_scenario

DEVICE_ID = "MACHINE_01"


def generate_energy() -> dict:
    scenario = get_demo_scenario()

    profiles = {
        "normal":       {"demand": 15.0, "solar": 10.0, "battery": 72.0, "load_pct": 65.0},
        "degrading":    {"demand": 20.0, "solar": 8.0,  "battery": 55.0, "load_pct": 78.0},
        "high_risk":    {"demand": 25.0, "solar": 6.0,  "battery": 35.0, "load_pct": 88.0},
        "critical":     {"demand": 28.0, "solar": 4.0,  "battery": 18.0, "load_pct": 95.0},
        "solar_surplus":{"demand": 10.0, "solar": 20.0, "battery": 85.0, "load_pct": 40.0},
        "peak_demand":  {"demand": 30.0, "solar": 5.0,  "battery": 28.0, "load_pct": 98.0},
        "energy_waste": {"demand": 27.0, "solar": 9.0,  "battery": 60.0, "load_pct": 35.0},
        "battery_low":  {"demand": 18.0, "solar": 3.0,  "battery":  8.0, "load_pct": 72.0},
        "grid_dependent":{"demand":22.0, "solar": 2.0,  "battery": 25.0, "load_pct": 85.0},
    }

    p = profiles.get(scenario, profiles["normal"])

    demand  = round(max(0.5, p["demand"]  + random.uniform(-1.5, 1.5)), 2)
    solar   = round(max(0.0, p["solar"]   + random.uniform(-1.0, 1.0)), 2)
    battery = round(max(0.0, min(100.0, p["battery"] + random.uniform(-1.0, 0.5))), 2)
    load_pct = round(max(0.0, min(100.0, p["load_pct"] + random.uniform(-3.0, 3.0))), 2)

    # Determine grid power (demand not covered by solar)
    grid_power = round(max(0.0, demand - solar), 2)

    # Power factor — slightly below 1.0 in normal operation
    power_factor = round(random.uniform(0.88, 0.99), 3)

    # Energy consumed this interval (1 second → convert kW to kWh)
    energy_consumed_kwh = round(demand / 3600.0, 6)

    # Battery charge rate — positive = charging, negative = discharging
    surplus = solar - demand
    if surplus > 0:
        charge_rate = round(min(surplus, 5.0), 2)       # charging up to 5 kW
    elif battery < 20:
        charge_rate = round(-min(demand * 0.3, 3.0), 2)  # discharging to cover demand
    else:
        charge_rate = 0.0

    return {
        "device_id":           DEVICE_ID,
        "timestamp":           datetime.now(timezone.utc).isoformat(),
        "power_consumption_kw":demand,
        "energy_consumed_kwh": energy_consumed_kwh,
        "solar_generation_kw": solar,
        "grid_power_kw":       grid_power,
        "battery_level":       battery,
        "battery_charge_rate": charge_rate,
        "load_percentage":     load_pct,
        "power_factor":        power_factor,
    }