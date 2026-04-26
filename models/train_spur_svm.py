"""
SPUR GEAR — SVM Model Training
GearMind AI · Elecon Engineering Works Pvt. Ltd.

Trains a dedicated SVM classifier + RUL regressor for spur gears.
Dataset: data/spur_gear_svm_dataset.csv
Features: Speed_RPM, Torque_Nm, Vibration_mm_s, Temperature_C, Shock_Load_g, Noise_dB
Target: Failure (0/1) → "No Failure" / "Failure"

Outputs:
  models/spur_svm_classifier.pkl
  models/spur_svm_scaler.pkl
  models/spur_svm_label_encoder.pkl
  models/spur_svm_rul_regressor.pkl
  models/spur_svm_scaler_rul.pkl
  xai/spur_shap_artifacts.pkl
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, f1_score, classification_report, roc_auc_score
from sklearn.ensemble import GradientBoostingRegressor

print("🔧 Spur Gear SVM Training Starting...")
print("=" * 55)

# ── Load Dataset ──────────────────────────────────────────
df = pd.read_csv('data/spur_gear_svm_dataset.csv')
print(f"   Dataset: {len(df)} rows x {len(df.columns)} columns")

SPUR_FEATURE_COLS = [
    'Speed_RPM', 'Torque_Nm', 'Vibration_mm_s',
    'Temperature_C', 'Shock_Load_g', 'Noise_dB'
]

# Map binary to meaningful labels
df['Fault_Label'] = df['Failure'].map({0: 'No Failure', 1: 'Failure'})

X_full = df[SPUR_FEATURE_COLS].values
y_full = df['Fault_Label'].values

# SVM is O(n^2) - subsample to 10K for feasible training
SAMPLE_SIZE = 10000
if len(df) > SAMPLE_SIZE:
    sss = StratifiedShuffleSplit(n_splits=1, train_size=SAMPLE_SIZE, random_state=42)
    sample_idx, _ = next(sss.split(X_full, y_full))
    X = X_full[sample_idx]
    y_labels = y_full[sample_idx]
    df_sample = df.iloc[sample_idx].reset_index(drop=True)
    print(f"   Subsampled to {SAMPLE_SIZE} rows for SVM feasibility")
else:
    X = X_full
    y_labels = y_full
    df_sample = df.reset_index(drop=True)

# Encode labels
le = LabelEncoder()
y = le.fit_transform(y_labels)
print(f"   Classes: {list(le.classes_)}")
print(f"   Distribution: No Failure={np.sum(y==list(le.classes_).index('No Failure'))}, Failure={np.sum(y==list(le.classes_).index('Failure'))}")

# ── Scale Features ────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Train/Test Split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# ── Train SVM ─────────────────────────────────────────────
print("\n   Training SVM (RBF kernel, probability=True)...")
svm_model = SVC(
    kernel='rbf',
    C=10.0,
    gamma='scale',
    probability=True,
    random_state=42,
    class_weight='balanced'
)
svm_model.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────
y_pred  = svm_model.predict(X_test)
y_proba = svm_model.predict_proba(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1       = f1_score(y_test, y_pred, average='weighted')
auc      = roc_auc_score(y_test, y_proba[:, 1])  # binary
cv_scores = cross_val_score(svm_model, X_scaled, y, cv=3, scoring='accuracy')

print(f"\n   Results:")
print(f"   Accuracy : {accuracy:.4f}")
print(f"   F1 Score : {f1:.4f}")
print(f"   AUC      : {auc:.4f}")
print(f"   CV Mean  : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=le.classes_)}")

# ── Synthetic RUL (vectorized) ────────────────────────────
print("   Generating synthetic RUL for spur gears...")
failure_probs = svm_model.predict_proba(X_scaled)
fail_col = list(le.classes_).index('Failure')

# Indices into SPUR_FEATURE_COLS
vib_i   = SPUR_FEATURE_COLS.index('Vibration_mm_s')
temp_i  = SPUR_FEATURE_COLS.index('Temperature_C')
shock_i = SPUR_FEATURE_COLS.index('Shock_Load_g')

fp_arr      = failure_probs[:, fail_col]
vib_arr     = np.clip(X[:, vib_i] / 10.0, 0, 1)
temp_arr    = np.clip((X[:, temp_i] - 40.0) / 60.0, 0, 1)
shock_arr   = np.clip(X[:, shock_i] / 5.0, 0, 1)
degradation = 0.4 * fp_arr + 0.2 * vib_arr + 0.2 * temp_arr + 0.2 * shock_arr
noise       = np.random.default_rng(42).uniform(0.85, 1.15, len(X))
rul_synthetic = np.maximum(0, (80000 * (1 - degradation) * noise)).astype(int)
print(f"   RUL range: {rul_synthetic.min()} – {rul_synthetic.max()} cycles")

# ── Train RUL Regressor ──────────────────────────────────
scaler_rul   = StandardScaler()
X_rul_scaled = scaler_rul.fit_transform(X)
rul_regressor = GradientBoostingRegressor(
    n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
)
rul_regressor.fit(X_rul_scaled, rul_synthetic)
print(f"   RUL R^2: {rul_regressor.score(X_rul_scaled, rul_synthetic):.4f}")

# ── Save Models ───────────────────────────────────────────
os.makedirs('models', exist_ok=True)
joblib.dump(svm_model,     'models/spur_svm_classifier.pkl')
joblib.dump(scaler,        'models/spur_svm_scaler.pkl')
joblib.dump(le,            'models/spur_svm_label_encoder.pkl')
joblib.dump(rul_regressor, 'models/spur_svm_rul_regressor.pkl')
joblib.dump(scaler_rul,    'models/spur_svm_scaler_rul.pkl')
print("\n   Spur SVM models saved.")

# ── Save Model Comparison ────────────────────────────────
json.dump({
    "SVM (RBF)": {
        "accuracy": float(accuracy), "f1": float(f1),
        "auc": float(auc), "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std())
    }
}, open('models/spur_model_comparison.json', 'w'), indent=2)

# ── SHAP Artifacts ────────────────────────────────────────
print("\n   Computing SHAP values for Spur SVM (KernelExplainer)...")
print("   This may take 2-3 minutes for SVM...")

try:
    import shap
    
    # Use smaller background sample for faster computation
    bg_idx = np.random.default_rng(0).choice(len(X_scaled), 50, replace=False)
    X_background = X_scaled[bg_idx]
    
    print(f"   Creating KernelExplainer with {len(X_background)} background samples...")
    explainer = shap.KernelExplainer(svm_model.predict_proba, X_background)
    
    # Test explainer with a single sample first
    print("   Testing explainer with single sample...")
    test_sample = X_scaled[0:1]
    test_shap = explainer.shap_values(test_sample, nsamples=50)
    print(f"   ✅ Explainer test successful! Output type: {type(test_shap)}")
    
    # Now compute for larger sample
    ex_idx = np.random.default_rng(1).choice(len(X_scaled), 100, replace=False)
    X_explain = X_scaled[ex_idx]
    
    print(f"   Computing SHAP for {len(X_explain)} samples (nsamples=50)...")
    shap_values = explainer.shap_values(X_explain, nsamples=50)
    
    print(f"   ✅ SHAP computation complete!")
    print(f"      SHAP values type: {type(shap_values)}")
    if isinstance(shap_values, list):
        print(f"      List with {len(shap_values)} elements")
        print(f"      First element shape: {shap_values[0].shape}")
    else:
        print(f"      Shape: {np.array(shap_values).shape}")
    
    os.makedirs('xai', exist_ok=True)
    
    # KernelExplainer can't be pickled due to Cython objects
    # Save only the data needed to recreate it
    print("   Saving SHAP artifacts (without explainer - will be recreated on demand)...")
    joblib.dump({
        'explainer': None,  # Can't pickle KernelExplainer
        'shap_values': shap_values,
        'X_sample': X_explain,
        'X_background': X_background,  # Save background for recreating explainer
        'feature_names': SPUR_FEATURE_COLS,
        'class_names': list(le.classes_),
        'model': svm_model,
        'scaler': scaler
    }, 'xai/spur_shap_artifacts.pkl')
    
    print("   ✅ Spur SHAP artifacts saved to xai/spur_shap_artifacts.pkl")
    print("   Note: Explainer will be recreated on-demand (KernelExplainer can't be pickled)")
    
except Exception as e:
    print(f"   ❌ SHAP computation failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n   ⚠️  WARNING: SHAP artifacts will NOT be available!")
    print("   The dashboard will show 'SHAP Analysis Unavailable' for Spur gear.")
    print("   This is not critical - the model will still work for predictions.")
    
    # Don't save broken artifacts - better to have no file than a broken one
    print("   Skipping SHAP artifacts save")


print("\n✅ Spur Gear SVM Training Complete!")
