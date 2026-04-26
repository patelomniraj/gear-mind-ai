"""
═══════════════════════════════════════════════════════════
BEVEL GEAR — Dedicated Model Training
GearMind AI · Elecon Engineering Works Pvt. Ltd.
═══════════════════════════════════════════════════════════

Trains a dedicated classifier + RUL regressor for bevel gears.
Dataset: data/bevel_gear_dataset.csv (classifier)
         data/bevel_rul_dataset.csv (RUL)

Features: Load (kN), Torque (Nm), Vibration RMS (mm/s),
          Temperature (°C), Wear (mm), Lubrication Index,
          Efficiency (%), Cycles in Use

Outputs:
  models/bevel_classifier.pkl
  models/bevel_scaler.pkl
  models/bevel_label_encoder.pkl
  models/bevel_rul_regressor.pkl
  models/bevel_scaler_rul.pkl
  xai/bevel_shap_artifacts.pkl
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, classification_report, roc_auc_score
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import xgboost as xgb

print("🔩 Bevel Gear Model Training Starting...")
print("=" * 55)

# ── Load Dataset ──────────────────────────────────────────
df = pd.read_csv('data/bevel_gear_dataset.csv')
df_rul = pd.read_csv('data/bevel_rul_dataset.csv')
print(f"   📊 Classifier Dataset: {len(df)} rows")
print(f"   📊 RUL Dataset: {len(df_rul)} rows")

BEVEL_FEATURE_COLS = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]

X = df[BEVEL_FEATURE_COLS].values
y_labels = df['Fault Label'].values

# Encode labels
le = LabelEncoder()
y = le.fit_transform(y_labels)
print(f"   Classes: {list(le.classes_)}")
print(f"   Distribution: {dict(zip(*np.unique(y_labels, return_counts=True)))}")

# ── Scale Features ────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Train/Test Split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# ── Train XGBoost Classifier ─────────────────────────────
print("\n   Training XGBoost Classifier for Bevel Gears...")
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1,
    use_label_encoder=False
)
xgb_model.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────
y_pred = xgb_model.predict(X_test)
y_proba = xgb_model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')
auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')
cv_scores = cross_val_score(xgb_model, X_scaled, y, cv=5, scoring='accuracy')

print(f"\n   📈 Results:")
print(f"   Accuracy:  {accuracy:.4f}")
print(f"   F1 Score:  {f1:.4f}")
print(f"   AUC:       {auc:.4f}")
print(f"   CV Mean:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=le.classes_)}")

# ── Train RUL Regressor ──────────────────────────────────
print("   Training Bevel RUL Regressor...")
X_rul = df_rul[BEVEL_FEATURE_COLS].values
y_rul = df_rul['RUL (cycles)'].values

scaler_rul = StandardScaler()
X_rul_scaled = scaler_rul.fit_transform(X_rul)

X_rul_train, X_rul_test, y_rul_train, y_rul_test = train_test_split(
    X_rul_scaled, y_rul, test_size=0.2, random_state=42
)

rul_model = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
rul_model.fit(X_rul_train, y_rul_train)

rul_r2_train = rul_model.score(X_rul_train, y_rul_train)
rul_r2_test = rul_model.score(X_rul_test, y_rul_test)
print(f"   RUL R² (train): {rul_r2_train:.4f}")
print(f"   RUL R² (test):  {rul_r2_test:.4f}")

# ── Save Models ───────────────────────────────────────────
os.makedirs('models', exist_ok=True)
joblib.dump(xgb_model, 'models/bevel_classifier.pkl')
joblib.dump(scaler, 'models/bevel_scaler.pkl')
joblib.dump(le, 'models/bevel_label_encoder.pkl')
joblib.dump(rul_model, 'models/bevel_rul_regressor.pkl')
joblib.dump(scaler_rul, 'models/bevel_scaler_rul.pkl')

print("\n   ✅ Bevel models saved:")
print("   models/bevel_classifier.pkl")
print("   models/bevel_scaler.pkl")
print("   models/bevel_label_encoder.pkl")
print("   models/bevel_rul_regressor.pkl")
print("   models/bevel_scaler_rul.pkl")

# ── Save Model Comparison ────────────────────────────────
bevel_comparison = {
    "XGBoost (Bevel)": {
        "accuracy": float(accuracy),
        "f1": float(f1),
        "auc": float(auc),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std())
    }
}
json.dump(bevel_comparison, open('models/bevel_model_comparison.json', 'w'), indent=2)

# ── SHAP Artifacts for Bevel ─────────────────────────────
print("\n   Computing SHAP values for Bevel gear...")
try:
    import shap

    # TreeExplainer works perfectly with XGBoost
    explainer = shap.TreeExplainer(xgb_model)

    # Compute on a sample of 2000 points
    sample_idx = np.random.choice(len(X_scaled), min(2000, len(X_scaled)), replace=False)
    X_sample = X_scaled[sample_idx]
    shap_values = explainer.shap_values(X_sample)

    os.makedirs('xai', exist_ok=True)
    joblib.dump({
        'explainer': explainer,
        'shap_values': shap_values,
        'X_sample': X_sample,
        'feature_names': BEVEL_FEATURE_COLS,
        'class_names': list(le.classes_),
        'model': xgb_model
    }, 'xai/bevel_shap_artifacts.pkl')

    print("   ✅ Bevel SHAP artifacts saved → xai/bevel_shap_artifacts.pkl")
except Exception as e:
    print(f"   ⚠ SHAP computation error: {e}")
    os.makedirs('xai', exist_ok=True)
    joblib.dump({
        'explainer': None,
        'shap_values': None,
        'X_sample': X_scaled[:2000],
        'feature_names': BEVEL_FEATURE_COLS,
        'class_names': list(le.classes_),
        'model': xgb_model
    }, 'xai/bevel_shap_artifacts.pkl')

print("\n✅ Bevel Gear Model Training Complete!")
print("🚀 Run next: uvicorn gear_api:app --reload --port 8000")
