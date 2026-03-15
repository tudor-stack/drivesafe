"""
DriveSafe — Behavior Classifier Training
Trains a lightweight model to classify driving behavior from sensor data.
Training time: ~30 seconds
"""
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

# --- 1. Generate synthetic training data -------------------------------------
np.random.seed(42)
N = 500  # samples per class

def make_samples(n, accel_range, speed_change_range, lateral_range, gyro_range, label):
    return [{
        "accel_magnitude_max": np.random.uniform(*accel_range),
        "speed_change_rate": np.random.uniform(*speed_change_range),
        "lateral_g": np.random.uniform(*lateral_range),
        "gyro_z_mean": np.random.uniform(*gyro_range),
        "speed_ms": np.random.uniform(5, 30),
        "label": label
    } for _ in range(n)]

data = (
    make_samples(N, (4.5, 9.0), (-9.0, -4.0), (0.0, 0.2), (0.0, 0.1), "hard_brake") +
    make_samples(N, (4.0, 8.0), (3.5, 8.0),   (0.0, 0.2), (0.0, 0.1), "aggressive_accel") +
    make_samples(N, (2.0, 5.0), (-2.0, 2.0),  (0.3, 0.8), (0.2, 0.6), "sharp_turn") +
    make_samples(N, (0.5, 2.5), (-1.5, 1.5),  (0.0, 0.15),(0.0, 0.05),"normal")
)

np.random.shuffle(data)

X = np.array([[
    d["accel_magnitude_max"],
    d["speed_change_rate"],
    d["lateral_g"],
    d["gyro_z_mean"],
    d["speed_ms"]
] for d in data])

y = np.array([d["label"] for d in data])

# --- 2. Train ----------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
model.fit(X_train, y_train)

# --- 3. Evaluate -------------------------------------------------------------
y_pred = model.predict(X_test)
print("\n=== DriveSafe Behavior Classifier ===")
print(classification_report(y_test, y_pred))

# --- 4. Save model -----------------------------------------------------------
os.makedirs("models", exist_ok=True)
with open("models/behavior_classifier.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved to models/behavior_classifier.pkl")

# --- 5. Quick inference test -------------------------------------------------
test_cases = [
    ([7.2, -6.5, 0.1, 0.02, 14.0], "hard_brake expected"),
    ([5.8,  4.8, 0.1, 0.02, 12.0], "aggressive_accel expected"),
    ([3.1,  0.5, 0.55, 0.35, 10.0], "sharp_turn expected"),
    ([1.2, -0.8, 0.05, 0.02, 8.0],  "normal expected"),
]

print("\n=== Inference Test ===")
for features, description in test_cases:
    prediction = model.predict([features])[0]
    confidence = max(model.predict_proba([features])[0]) * 100
    print(f"{description:35} -> {prediction:20} ({confidence:.1f}% confidence)")
