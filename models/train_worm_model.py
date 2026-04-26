"""
WORM GEAR — Logistic Regression Model Training
GearMind AI · Elecon Engineering Works Pvt. Ltd.

Trains a dedicated Logistic Regression classifier + RUL regressor for worm gears.
Dataset: data/worm_gear_dataset.csv
Features: Worm_RPM, Input_Torque, Output_Torque, Motor_Current, Oil_Temp, Ambient_Temp,
          Axial_Vib, Radial_Vib, Cu_PPM, Fe_PPM, Efficiency_Calc, Friction_Coeff, Backlash
Target: Failure_Label → "No Fault" / "Minor Fault" / "Major Fault"

Outputs:
  models/worm_classifier.pkl
  models/worm_scaler.pkl
  models/worm_label_encoder.pkl
  models/worm_rul_regressor.pkl
  models/worm_scaler_rul.pkl
  models/worm_model_comparison.json
  xai/worm_shap_artifacts.pkl
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, classification_report, roc_auc_score
from sklearn.ensemble import GradientBoostingRegressor

print("🌀 Worm Gear Logistic Regression Training Starting...")
print("=" * 60)

# ── Load Dataset ──────────────────────────────────────────
df = pd.read_csv('../data/worm_gear_dataset.csv')
print(f"   Dataset: {len(df)} rows x {len(df.columns)} columns")

WORM_FEATURE_COLS = [
    'Worm_RPM', 'Input_Torque', 'Output_Torque', 'Motor_Current',
    'Oil_Temp', 'Ambient_Temp', 'Axial_Vib', 'Radial_Vib',
    'Cu_PPM', 'Fe_PPM', 'Efficiency_Calc', 'Friction_Coeff', 'Backlash'
]

X = df[WORM_FEATURE_COLS].values
y_labels = df['Failure_Label'].values

# Encode labels
le = LabelEncoder()
y = le.fit_transform(y_labels)
print(f"   Classes: {list(le.classes_)}")
print(f"   Distribution:")
for cls in le.classes_:
    count = np.sum(y_labels == cls)
    print(f"      {cls}: {count} ({count/len(y)*100:.1f}%)")

# ── Scale Features ────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Train/Test Split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# ── Train Logistic Regression ─────────────────────────────
print("\n   Training Logistic Regression (multi-class, L2 penalty)...")
lr_model = LogisticRegression(
    multi_class='multinomial',
    solver='lbfgs',
    C=1.0,
    max_iter=1000,
    random_state=42,
    class_weight='balanced'
)
lr_model.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────
y_pred  = lr_model.predict(X_test)
y_proba = lr_model.predict_proba(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1       = f1_score(y_test, y_pred, average='weighted')

# Multi-class AUC (one-vs-rest)
try:
    from sklearn.preprocessing import label_binarize
    y_test_bin = label_binarize(y_test, classes=range(len(le.classes_)))
    auc = roc_auc_score(y_test_bin, y_proba, average='weighted', multi_class='ovr')
except:
    auc = 0.0

cv_scores = cross_val_score(lr_model, X_scaled, y, cv=5, scoring='accuracy')

print(f"\n   Results:")
print(f"   Accuracy : {accuracy:.4f}")
print(f"   F1 Score : {f1:.4f}")
print(f"   AUC      : {auc:.4f}")
print(f"   CV Mean  : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=le.classes_)}")

# ── Use Existing RUL from Dataset ────────────────────────
print("   Using RUL_Cycles from dataset...")
rul_values = df['RUL_Cycles'].values
print(f"   RUL range: {rul_values.min()} – {rul_values.max()} cycles")

# ── Train RUL Regressor ──────────────────────────────────
scaler_rul   = StandardScaler()
X_rul_scaled = scaler_rul.fit_transform(X)
rul_regressor = GradientBoostingRegressor(
    n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42
)
rul_regressor.fit(X_rul_scaled, rul_values)
rul_r2 = rul_regressor.score(X_rul_scaled, rul_values)
print(f"   RUL R^2: {rul_r2:.4f}")

# ── Save Models ───────────────────────────────────────────
os.makedirs('models', exist_ok=True)
joblib.dump(lr_model,      'models/worm_classifier.pkl')
joblib.dump(scaler,        'models/worm_scaler.pkl')
joblib.dump(le,            'models/worm_label_encoder.pkl')
joblib.dump(rul_regressor, 'models/worm_rul_regressor.pkl')
joblib.dump(scaler_rul,    'models/worm_scaler_rul.pkl')
print("\n   Worm Gear models saved.")

# ── Save Model Comparison ────────────────────────────────
json.dump({
    "Logistic Regression": {
        "accuracy": float(accuracy), "f1": float(f1),
        "auc": float(auc), "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()), "rul_r2": float(rul_r2)
    }
}, open('models/worm_model_comparison.json', 'w'), indent=2)

# ── SHAP Artifacts ────────────────────────────────────────
print("\n   Computing SHAP values for Worm Gear (LinearExplainer)...")

try:
    import shap
    
    # Use smaller sample for SHAP
    ex_idx = np.random.default_rng(1).choice(len(X_scaled), min(500, len(X_scaled)), replace=False)
    X_explain = X_scaled[ex_idx]
    
    print(f"   Creating LinearExplainer...")
    explainer = shap.LinearExplainer(lr_model, X_scaled)
    
    print(f"   Computing SHAP for {len(X_explain)} samples...")
    shap_values = explainer.shap_values(X_explain)
    
    print(f"   ✅ SHAP computation complete!")
    print(f"      SHAP values type: {type(shap_values)}")
    if isinstance(shap_values, list):
        print(f"      List with {len(shap_values)} elements (one per class)")
        print(f"      First element shape: {shap_values[0].shape}")
    else:
        print(f"      Shape: {np.array(shap_values).shape}")
    
    os.makedirs('xai', exist_ok=True)
    
    joblib.dump({
        'explainer': explainer,
        'shap_values': shap_values,
        'X_sample': X_explain,
        'feature_names': WORM_FEATURE_COLS,
        'class_names': list(le.classes_)
    }, 'xai/worm_shap_artifacts.pkl')
    
    print("   ✅ Worm SHAP artifacts saved to xai/worm_shap_artifacts.pkl")
    
except Exception as e:
    print(f"   ❌ SHAP computation failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n   ⚠️  WARNING: SHAP artifacts will NOT be available!")
    print("   The dashboard will show 'SHAP Analysis Unavailable' for Worm gear.")
    print("   This is not critical - the model will still work for predictions.")

print("\n✅ Worm Gear Logistic Regression Training Complete!")
print("=" * 60)
print("\nNext steps:")
print("  1. Run the API: uvicorn gear_api:app --reload --port 8000")
print("  2. Test worm gear predictions via /api/predict endpoint")
print("  3. Verify SHAP visualizations in the dashboard")
