import random
import uuid
from datetime import datetime, timezone
from backend.utils.config import get_demo_scenario

DEVICE_ID = "MACHINE_01"

CURRENCIES = ["INR", "USD", "EUR"]
CATEGORIES = ["RETAIL", "FUEL", "FOOD", "UTILITIES", "ELECTRONICS", "TRANSFER", "ATM"]
LOCATIONS  = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune"]
DEVICES    = ["device_primary", "device_secondary", "device_new_unknown"]

NORMAL_AMOUNTS = [250, 480, 750, 1200, 1800, 2500]
HIGH_AMOUNTS   = [48000, 72000, 95000, 150000]


def generate_transaction() -> dict:
    scenario = get_demo_scenario()

    profiles = {
        "normal":               {"amount_pool": NORMAL_AMOUNTS, "location": LOCATIONS[0], "device": DEVICES[0], "rapid": False},
        "high_risk":            {"amount_pool": HIGH_AMOUNTS,   "location": LOCATIONS[2], "device": DEVICES[2], "rapid": True},
        "critical":             {"amount_pool": HIGH_AMOUNTS,   "location": LOCATIONS[5], "device": DEVICES[2], "rapid": True},
        "suspicious_pattern":   {"amount_pool": HIGH_AMOUNTS,   "location": LOCATIONS[4], "device": DEVICES[2], "rapid": True},
        "degrading":            {"amount_pool": NORMAL_AMOUNTS, "location": LOCATIONS[1], "device": DEVICES[1], "rapid": False},
    }

    p = profiles.get(scenario, profiles["normal"])

    amount   = round(random.choice(p["amount_pool"]) + random.uniform(-50, 50), 2)
    location = p["location"] if random.random() > 0.2 else random.choice(LOCATIONS)
    device   = p["device"]   if random.random() > 0.15 else random.choice(DEVICES)

    return {
        "transaction_id":    str(uuid.uuid4())[:12].upper(),
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "user_id":           "demo_user_001",
        "amount":            max(1.0, amount),
        "currency":          "INR",
        "transaction_type":  random.choice(["DEBIT", "CREDIT", "TRANSFER"]),
        "merchant_category": random.choice(CATEGORIES),
        "location":          location,
        "device_id":         device,
        "is_rapid":          p["rapid"],
    }