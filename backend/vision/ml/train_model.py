# train_model.py — trains and saves the predictive maintenance classifier

from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from backend.vision.ml.generate_training_data import generate_dataset


FEATURES = [
    "temperature",
    "vibration",
    "rpm",
    "battery",
    "temp_slope",
    "vib_slope",
    "rpm_instability",
    "anomaly_rate",
]


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "predictive_maintenance.joblib"
)


def train() -> None:
    print("Generating training data...")

    df = generate_dataset()

    X = df[FEATURES].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Training RandomForestClassifier...")

    clf = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )

    clf.fit(X_train, y_train)

    print("\nEvaluation:")

    print(
        classification_report(
            y_test,
            clf.predict(X_test),
            target_names=[
                "healthy",
                "degrading",
                "high_risk",
                "critical",
            ],
        )
    )

    # Create the models directory
    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save both the trained model and feature names
    joblib.dump(
        {
            "model": clf,
            "features": FEATURES,
        },
        MODEL_PATH,
    )

    print(f"\nModel saved → {MODEL_PATH}")


if __name__ == "__main__":
    train()