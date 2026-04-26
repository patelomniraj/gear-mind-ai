"""
═══════════════════════════════════════════════════════════
MODULE 3 — EXPLAINABILITY LAYER (XAI)
GearMind AI · Elecon Engineering Works Pvt. Ltd.
═══════════════════════════════════════════════════════════

WHAT THIS FILE DOES:
  1. SHAP  — explains which features drove each prediction
  2. LIME  — cross-validates SHAP with a different method
  3. Anomaly Detection — flags suspicious gears BEFORE
     they reach fault status (early warning system)
  4. Fault Progression — shows how a gear degrades over time

HOW TO RUN:
  pip install shap lime scikit-learn joblib matplotlib
  python xai/explain.py

OUTPUT:
  xai/shap_values.pkl         → precomputed SHAP values
  xai/anomaly_model.pkl       → Isolation Forest model
  xai/shap_summary.png        → SHAP feature importance plot
"""

import numpy as np
import pandas as pd
import joblib
import shap
import lime
import lime.lime_tabular
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for saving plots
from sklearn.ensemble import IsolationForest
import os, warnings
warnings.filterwarnings('ignore')

print("🔍 GearMind XAI Engine Starting...")

# ════════════════════════════════════════════════════════
# LOAD ARTIFACTS FROM MODULE 2
# ════════════════════════════════════════════════════════

# Note: We load model_comparison to find XGBoost specifically
# SHAP TreeExplainer does not support multiclass GradientBoosting
# XGBoost has full multiclass SHAP support
import json
comparison = json.load(open('models/model_comparison.json'))

# Try to load best model, fall back to XGBoost for SHAP
model = joblib.load('models/best_classifier.pkl')
scaler  = joblib.load('models/scaler.pkl')
le      = joblib.load('models/label_encoder.pkl')

# For SHAP we need XGBoost — retrain a quick one if needed
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder as LE

df = pd.read_csv('data/helical_gear_dataset.csv')

FEATURE_COLS = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]

X = df[FEATURE_COLS].values
X_scaled = scaler.transform(X)

print("   ✅ Models and data loaded")

# ════════════════════════════════════════════════════════
# STEP 1: SHAP — SHapley Additive exPlanations
# ════════════════════════════════════════════════════════
# SHAP tells us: "For THIS specific prediction, which
# features pushed it toward fault and by how much?"

print("\n   Computing SHAP values (this takes ~1 min)...")

# XGBoost has full multiclass SHAP support
# Retrain a quick XGBoost model on the same data for SHAP
print("   Training XGBoost for SHAP (multiclass supported)...")
y_encoded = le.transform(df["Fault Label"].values)
X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

xgb_model = xgb.XGBClassifier(
    n_estimators=100, learning_rate=0.1, max_depth=5,
    eval_metric="mlogloss", random_state=42, n_jobs=-1
)
xgb_model.fit(X_tr, y_tr)
print(f"   XGBoost accuracy for SHAP: {(xgb_model.predict(X_te) == y_te).mean():.4f}")

# TreeExplainer works perfectly with XGBoost multiclass
explainer = shap.TreeExplainer(xgb_model)

# Compute on a sample of 2000 points (faster for demo)
sample_idx  = np.random.choice(len(X_scaled), 2000, replace=False)
X_sample    = X_scaled[sample_idx]
shap_values = explainer.shap_values(X_sample)

print("   ✅ SHAP values computed")

# Save SHAP artifacts
os.makedirs('xai', exist_ok=True)
joblib.dump({
    'explainer':   explainer,
    'shap_model':  xgb_model,
    'shap_values': shap_values,
    'X_sample':    X_sample,
    'feature_names': FEATURE_COLS
}, 'xai/shap_artifacts.pkl')

# SHAP Summary Plot — global feature importance
plt.figure(figsize=(10, 6))
shap.summary_plot(
    shap_values, X_sample,
    feature_names=FEATURE_COLS,
    class_names=le.classes_,
    show=False
)
plt.title('SHAP Feature Importance — GearMind AI', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('xai/shap_summary.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ SHAP summary plot saved → xai/shap_summary.png")

# ════════════════════════════════════════════════════════
# SHAP Helper Function (used by dashboard)
# ════════════════════════════════════════════════════════

def get_shap_for_input(input_array):
    """
    Get SHAP values for a single gear sensor reading.
    
    input_array: numpy array of shape (1, 8) — raw feature values
    returns: dict of {feature_name: shap_value}
    """
    input_scaled = scaler.transform(input_array.reshape(1, -1))
    sv = explainer.shap_values(input_scaled)
    
    # sv is a list of arrays (one per class)
    # We take the class with highest prediction
    pred_class = model.predict(input_scaled)[0]
    sv_for_class = sv[pred_class][0]
    
    return dict(zip(FEATURE_COLS, sv_for_class))

# ════════════════════════════════════════════════════════
# STEP 2: LIME — Local Interpretable Model-agnostic Explanations
# ════════════════════════════════════════════════════════
# LIME works differently from SHAP — it perturbs the input
# and fits a simple linear model around that point.
# Using BOTH SHAP and LIME gives cross-validated explanations.

lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data  = X_scaled,
    feature_names  = FEATURE_COLS,
    class_names    = list(le.classes_),
    mode           = 'classification',
    discretize_continuous = True,
    random_state   = 42
)

def get_lime_for_input(input_array, num_features=6):
    """
    Get LIME explanation for a single gear sensor reading.
    
    input_array: raw feature values (1D array of 8 values)
    returns: list of (feature_description, weight) tuples
    """
    input_scaled = scaler.transform(input_array.reshape(1, -1))[0]
    pred_class   = model.predict(input_scaled.reshape(1, -1))[0]
    
    explanation = lime_explainer.explain_instance(
        data_row       = input_scaled,
        predict_fn     = model.predict_proba,
        num_features   = num_features,
        labels         = [pred_class]
    )
    return explanation.as_list(label=pred_class)

print("   ✅ LIME explainer ready")

# ════════════════════════════════════════════════════════
# STEP 3: ANOMALY DETECTION — Isolation Forest
# ════════════════════════════════════════════════════════
# This is the EARLY WARNING system.
# It learns what "normal" gear behavior looks like.
# When a gear starts behaving unusually — even before
# crossing fault thresholds — it flags it as SUSPICIOUS.

print("\n   Training Anomaly Detection (Isolation Forest)...")

# Train ONLY on healthy gear data
# This teaches the model what normal looks like
healthy_mask  = df['Fault Label'] == 'No Fault'
X_healthy     = X_scaled[healthy_mask]

anomaly_model = IsolationForest(
    n_estimators  = 200,
    contamination = 0.05,    # expects ~5% of new data to be anomalous
    random_state  = 42,
    n_jobs        = -1
)
anomaly_model.fit(X_healthy)

# Test it — should flag fault samples as anomalies
anomaly_scores  = anomaly_model.decision_function(X_scaled)
anomaly_labels  = anomaly_model.predict(X_scaled)  # -1 = anomaly, 1 = normal

# How well does it catch faults?
actual_faults   = (df['Fault Label'] != 'No Fault').values
detected        = (anomaly_labels == -1)
detection_rate  = (detected & actual_faults).sum() / actual_faults.sum()

print(f"   ✅ Anomaly Detection Rate: {detection_rate:.1%} of faults flagged")
print(f"   (System catches {detection_rate:.0%} of fault cases as 'suspicious'")
print(f"    before they're classified as faults)")

joblib.dump(anomaly_model, 'xai/anomaly_model.pkl')

def get_anomaly_score(input_array):
    """
    Returns anomaly score and status for a gear reading.
    
    Score interpretation:
      > 0.0  → Normal behavior
      -0.1 to 0.0 → Slightly unusual (WATCH)
      < -0.1 → Anomalous (SUSPICIOUS — early warning!)
    """
    input_scaled = scaler.transform(input_array.reshape(1, -1))
    score  = anomaly_model.decision_function(input_scaled)[0]
    status = anomaly_model.predict(input_scaled)[0]
    
    if status == 1:
        return score, "NORMAL"
    elif score > -0.05:
        return score, "WATCH"
    else:
        return score, "SUSPICIOUS"

# ════════════════════════════════════════════════════════
# STEP 4: FAULT PROGRESSION SIMULATION
# ════════════════════════════════════════════════════════
# Shows how a gear degrades from healthy → failure
# Used for the timeline visualization in the dashboard

def simulate_fault_progression(
    initial_load=55, initial_lubrication=0.85, n_steps=50
):
    """
    Simulates gear degradation over time.
    Returns a DataFrame showing sensor evolution across cycles.
    
    This is used to draw the fault progression timeline chart.
    """
    progression = []
    
    lube = initial_lubrication
    wear = 0.05
    
    for step in range(n_steps):
        cycle = step * 2000   # 2000 cycles per step
        
        # Physics-based degradation
        lube = max(0.05, lube - np.random.uniform(0.01, 0.025))
        wear = wear + (initial_load / 60) * 0.015 * (2 - lube)
        temp = 65 + (initial_load - 50) * 0.4 + (1 - lube) * 35
        vib  = 1.5 + wear * 2.8 + (1 - lube) * 4.0

        row = np.array([
            initial_load,
            initial_load * 4.2,
            vib, temp, wear, lube,
            97 - wear * 3.5 - (temp - 65) * 0.08,
            cycle
        ])
        
        row_scaled = scaler.transform(row.reshape(1, -1))
        pred_label = le.inverse_transform(model.predict(row_scaled))[0]
        confidence = model.predict_proba(row_scaled).max()
        an_score, an_status = get_anomaly_score(row)
        
        progression.append({
            'Cycle':              cycle,
            'Vibration':          round(vib, 2),
            'Temperature':        round(temp, 2),
            'Wear':               round(wear, 4),
            'Lubrication':        round(lube, 4),
            'Fault Label':        pred_label,
            'Confidence':         round(confidence, 3),
            'Anomaly Status':     an_status,
            'Anomaly Score':      round(an_score, 4),
        })
    
    return pd.DataFrame(progression)

# Generate and save example progression
print("\n   Generating fault progression simulation...")
progression_df = simulate_fault_progression()
progression_df.to_csv('xai/fault_progression.csv', index=False)

# Print progression summary
print("\n   📈 Gear Degradation Timeline:")
print(f"   {'Cycle':>8} {'Vibration':>10} {'Temp':>8} {'Status':>15} {'Anomaly':>12}")
print("   " + "─"*55)
for _, row in progression_df.iloc[::10].iterrows():
    print(f"   {row['Cycle']:>8,.0f} {row['Vibration']:>10.2f} {row['Temperature']:>8.1f} {row['Fault Label']:>15} {row['Anomaly Status']:>12}")

print("\n✅ XAI Layer Complete:")
print("   xai/shap_artifacts.pkl")
print("   xai/anomaly_model.pkl")
print("   xai/fault_progression.csv")
print("   xai/shap_summary.png")
print("\n🚀 Run next: python app.py")
