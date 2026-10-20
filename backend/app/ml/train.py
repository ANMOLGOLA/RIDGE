import os
import json
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, confusion_matrix
from app.ml.synth_data import generate_synthetic_training_data
from app.ml.features import FEATURE_NAMES

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "models", "risk_xgb.joblib")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "models", "metrics.json")

def train_model():
    print("Generating synthetic training data for RIDGE Risk Engine...")
    df = generate_synthetic_training_data(n_samples=4000)

    X = df[FEATURE_NAMES]
    y = df["disruption_label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training XGBoost Classifier...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    auc = float(roc_auc_score(y_test, y_pred_proba))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature Importance
    importances = {
        feat: float(imp)
        for feat, imp in zip(FEATURE_NAMES, model.feature_importances_)
    }
    # Sort descending
    importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    metrics = {
        "roc_auc": round(auc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "confusion_matrix": cm,
        "feature_importances": importances,
        "dataset_size": len(df),
        "notes": "Model trained on synthetic data for the prototype. Replace with historical incident data for production."
    }

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model saved to {MODEL_PATH}")
    print(f"Metrics saved to {METRICS_PATH}")
    print(f"Results: AUC={auc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}")
    return model, metrics

if __name__ == "__main__":
    train_model()
