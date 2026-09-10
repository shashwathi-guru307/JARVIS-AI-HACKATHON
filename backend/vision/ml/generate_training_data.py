# generate_training_data.py — creates labelled synthetic machine-degradation data
import numpy as np
import pandas as pd
from pathlib import Path


SCENARIOS = {
    "healthy":   {"temp_base": 72, "vib_base": 0.28, "rpm_base": 1800, "bat_base": 90, "label": 0},
    "degrading": {"temp_base": 82, "vib_base": 0.55, "rpm_base": 1950, "bat_base": 70, "label": 1},
    "high_risk": {"temp_base": 91, "vib_base": 0.78, "rpm_base": 2150, "bat_base": 45, "label": 2},
    "critical":  {"temp_base": 97, "vib_base": 0.97, "rpm_base": 2380, "bat_base": 22, "label": 3},
}

SAMPLES_PER_SCENARIO = 500


def generate_dataset() -> pd.DataFrame:
    rows = []
    for name, cfg in SCENARIOS.items():
        for _ in range(SAMPLES_PER_SCENARIO):
            temp = cfg["temp_base"] + np.random.normal(0, 3)
            vib  = cfg["vib_base"]  + np.random.normal(0, 0.05)
            rpm  = cfg["rpm_base"]  + np.random.normal(0, 80)
            bat  = cfg["bat_base"]  + np.random.normal(0, 4)

            rows.append({
                "temperature":    max(55.0, min(105.0, temp)),
                "vibration":      max(0.0,  min(1.4,   vib)),
                "rpm":            max(800.0, min(2600.0, rpm)),
                "battery":        max(0.0,  min(100.0,  bat)),
                "temp_slope":     np.random.uniform(-0.1, 0.5) if cfg["label"] > 0 else np.random.uniform(-0.05, 0.05),
                "vib_slope":      np.random.uniform(-0.001, 0.01) if cfg["label"] > 0 else np.random.uniform(-0.001, 0.001),
                "rpm_instability": min(cfg["label"] * 0.15 + abs(np.random.normal(0, 0.05)), 1.0),
                "anomaly_rate":   min(cfg["label"] * 0.12 + abs(np.random.normal(0, 0.03)), 1.0),
                "label":          cfg["label"],
                "scenario":       name,
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_dataset()
    out = Path("ml/models")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "training_data.csv", index=False)
    print(f"Generated {len(df)} training samples → ml/models/training_data.csv")