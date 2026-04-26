"""
Complete Training for Spur and Bevel Gears - 5 Models Each
Matches Helical and Worm gear approach
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import label_binarize

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except:
    HAS_XGBOOST = False
    print("⚠️  XGBoost not installed")

print("=" * 80)
print("🚀 TRAINING SPUR AND BEVEL GEARS - 5 MODELS EACH")
print("=" * 80)

def get_models():
    """Return 5 models for training."""
    models = {
        'Logistic Regression': LogisticRegression(
            multi_class='multinomial', solver='lbfgs', C=1.0,
            max_iter=1000, random_state=42, class_weight='balanced'
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=150, max_depth=12, min_samples_split=5,
            random_state=42, class_weight='balanced', n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.1,
            random_state=42, subsample=0.8
        ),
        'SVM (RBF)': SVC(
            kernel='rbf', C=10.0, gamma='scale',
            probability=True, random_state=42, class_weight='balanced'
        )
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = xgb.XGBClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.1,
            random_state=42, eval_metric='logloss', use_label_encoder=False,
            n_jobs=-1
        )
    
    return models

# ═══════════════════════════════════════════════════════════
# TRAIN SPUR GEAR
# ═══════════════════════════════════════════════════════════

print(f"\n{'=' * 80}")
print("🔧 TRAINING SPUR GEAR MODELS")
print(f"{'=' * 80}")

# Load spur dataset
df_spur = pd.read_csv('data/spur_gear_svm_dataset.csv')
print(f"   Dataset: {len(df_spur)} rows x {len(df_spur.columns)} columns")

SPUR_FEATURES = ['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 'Temperature_C', 'Shock_Load_g', 'Noise_dB']
X_spur = df_spur[SPUR_FEATURES].values
y_spur_binary = df_spur['Failure'].values

# Convert binary to 3-class for consistency
# 0 = No Failure, 1 = Failure
# We'll create: No Failure, Minor Failure, Major Failure based on sensor thresholds
def create_spur_labels(df):
    """Create 3-class labels for spur based on severity."""
    labels = []
    for _, row in df.iterrows():
        if row['Failure'] == 0:
            labels.append('No Failure')
        else:
            # Use vibration and temperature to determine severity
            if row['Vibration_mm_s'] > 12 or row['Temperature_C'] > 95:
                labels.append('Major Failure')
            else:
                labels.append('Minor Failure')
    return np.array(labels)

y_spur_labels = create_spur_labels(df_spur)
print(f"   Created 3-class labels from binary failure")

# Encode labels
le_spur = LabelEncoder()
y_spur = le_spur.fit_transform(y_spur_labels)
print(f"   Classes: {list(le_spur.classes_)}")
for cls in le_spur.classes_:
    count = np.sum(y_spur_labels == cls)
    print(f"      {cls}: {count} ({count/len(y_spur)*100:.1f}%)")

# Scale features
scaler_spur = StandardScaler()
X_spur_scaled = scaler_spur.fit_transform(X_spur)

# Train/test split
X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X_spur_scaled, y_spur, test_size=0.2, random_state=42, stratify=y_spur
)

# Train RUL regressor
print(f"\n   Training RUL Regressor...")
# Generate RUL based on failure status and sensor values
rul_spur = np.where(y_spur_labels == 'No Failure',
                    np.random.randint(40000, 80000, len(y_spur_labels)),
                    np.where(y_spur_labels == 'Minor Failure',
                            np.random.randint(10000, 40000, len(y_spur_labels)),
                            np.random.randint(1000, 10000, len(y_spur_labels))))

scaler_rul_spur = StandardScaler()
X_rul_spur_scaled = scaler_rul_spur.fit_transform(X_spur)
rul_regressor_spur = GradientBoostingRegressor(
    n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42
)
rul_regressor_spur.fit(X_rul_spur_scaled, rul_spur)
rul_r2_spur = rul_regressor_spur.score(X_rul_spur_scaled, rul_spur)
print(f"   RUL R²: {rul_r2_spur:.4f}")

# Save preprocessing
os.makedirs('models', exist_ok=True)
joblib.dump(scaler_spur, 'models/spur_scaler.pkl')
joblib.dump(le_spur, 'models/spur_label_encoder.pkl')
joblib.dump(rul_regressor_spur, 'models/spur_rul_regressor.pkl')
joblib.dump(scaler_rul_spur, 'models/spur_scaler_rul.pkl')

# Train all models
models_spur = get_models()
comparison_spur = {}
best_model_spur = None
best_auc_spur = 0.0

for model_name, model in models_spur.items():
    print(f"\n   Training {model_name}...")
    
    model.fit(X_train_s, y_train_s)
    y_pred_s = model.predict(X_test_s)
    y_proba_s = model.predict_proba(X_test_s)
    
    accuracy = accuracy_score(y_test_s, y_pred_s)
    f1 = f1_score(y_test_s, y_pred_s, average='weighted')
    
    try:
        y_test_bin = label_binarize(y_test_s, classes=range(len(le_spur.classes_)))
        auc = roc_auc_score(y_test_bin, y_proba_s, average='weighted', multi_class='ovr')
    except:
        auc = 0.0
    
    cv_scores = cross_val_score(model, X_spur_scaled, y_spur, cv=5, scoring='accuracy')
    
    print(f"      Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}, CV: {cv_scores.mean():.4f}")
    
    # Save model
    model_filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    joblib.dump(model, f'models/spur_classifier_{model_filename}.pkl')
    
    comparison_spur[model_name] = {
        'accuracy': float(accuracy),
        'f1': float(f1),
        'auc': float(auc),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std())
    }
    
    if auc > best_auc_spur:
        best_auc_spur = auc
        best_model_spur = (model_name, model)

# Save comparison
json.dump(comparison_spur, open('models/spur_model_comparison.json', 'w'), indent=2)

# Save best model as default
if best_model_spur:
    joblib.dump(best_model_spur[1], 'models/spur_classifier.pkl')
    print(f"\n   ✅ Best: {best_model_spur[0]} (AUC: {best_auc_spur:.4f})")

# SHAP for best model
print(f"\n   Computing SHAP values...")
try:
    import shap
    ex_idx = np.random.default_rng(1).choice(len(X_spur_scaled), min(500, len(X_spur_scaled)), replace=False)
    X_explain_s = X_spur_scaled[ex_idx]
    
    if 'Logistic' in best_model_spur[0] or 'SVM' in best_model_spur[0]:
        explainer_s = shap.LinearExplainer(best_model_spur[1], X_spur_scaled)
    else:
        explainer_s = shap.TreeExplainer(best_model_spur[1])
    
    shap_values_s = explainer_s.shap_values(X_explain_s)
    
    os.makedirs('xai', exist_ok=True)
    joblib.dump({
        'explainer': explainer_s,
        'shap_values': shap_values_s,
        'X_sample': X_explain_s,
        'feature_names': SPUR_FEATURES,
        'class_names': list(le_spur.classes_),
        'model_name': best_model_spur[0]
    }, 'xai/spur_shap_artifacts.pkl')
    
    print(f"   ✅ SHAP artifacts saved")
except Exception as e:
    print(f"   ⚠️  SHAP failed: {e}")

print(f"\n✅ SPUR GEAR TRAINING COMPLETE!")

# ═══════════════════════════════════════════════════════════
# TRAIN BEVEL GEAR
# ═══════════════════════════════════════════════════════════

print(f"\n{'=' * 80}")
print("🔩 TRAINING BEVEL GEAR MODELS")
print(f"{'=' * 80}")

# Load bevel dataset
df_bevel = pd.read_csv('data/bevel_rul_dataset.csv')
print(f"   Dataset: {len(df_bevel)} rows x {len(df_bevel.columns)} columns")

BEVEL_FEATURES = ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)', 
                  'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use']
X_bevel = df_bevel[BEVEL_FEATURES].values
rul_bevel = df_bevel['RUL (cycles)'].values

# Create failure labels from RUL
y_bevel_labels = np.where(rul_bevel > 50000, 'No Fault',
                          np.where(rul_bevel > 20000, 'Minor Fault', 'Major Fault'))
print(f"   Created failure labels from RUL")

# Encode labels
le_bevel = LabelEncoder()
y_bevel = le_bevel.fit_transform(y_bevel_labels)
print(f"   Classes: {list(le_bevel.classes_)}")
for cls in le_bevel.classes_:
    count = np.sum(y_bevel_labels == cls)
    print(f"      {cls}: {count} ({count/len(y_bevel)*100:.1f}%)")

# Scale features
scaler_bevel = StandardScaler()
X_bevel_scaled = scaler_bevel.fit_transform(X_bevel)

# Train/test split
X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X_bevel_scaled, y_bevel, test_size=0.2, random_state=42, stratify=y_bevel
)

# Train RUL regressor
print(f"\n   Training RUL Regressor...")
scaler_rul_bevel = StandardScaler()
X_rul_bevel_scaled = scaler_rul_bevel.fit_transform(X_bevel)
rul_regressor_bevel = GradientBoostingRegressor(
    n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42
)
rul_regressor_bevel.fit(X_rul_bevel_scaled, rul_bevel)
rul_r2_bevel = rul_regressor_bevel.score(X_rul_bevel_scaled, rul_bevel)
print(f"   RUL R²: {rul_r2_bevel:.4f}")

# Save preprocessing
joblib.dump(scaler_bevel, 'models/bevel_scaler.pkl')
joblib.dump(le_bevel, 'models/bevel_label_encoder.pkl')
joblib.dump(rul_regressor_bevel, 'models/bevel_rul_regressor.pkl')
joblib.dump(scaler_rul_bevel, 'models/bevel_scaler_rul.pkl')

# Train all models
models_bevel = get_models()
comparison_bevel = {}
best_model_bevel = None
best_auc_bevel = 0.0

for model_name, model in models_bevel.items():
    print(f"\n   Training {model_name}...")
    
    model.fit(X_train_b, y_train_b)
    y_pred_b = model.predict(X_test_b)
    y_proba_b = model.predict_proba(X_test_b)
    
    accuracy = accuracy_score(y_test_b, y_pred_b)
    f1 = f1_score(y_test_b, y_pred_b, average='weighted')
    
    try:
        y_test_bin = label_binarize(y_test_b, classes=range(len(le_bevel.classes_)))
        auc = roc_auc_score(y_test_bin, y_proba_b, average='weighted', multi_class='ovr')
    except:
        auc = 0.0
    
    cv_scores = cross_val_score(model, X_bevel_scaled, y_bevel, cv=5, scoring='accuracy')
    
    print(f"      Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}, CV: {cv_scores.mean():.4f}")
    
    # Save model
    model_filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    joblib.dump(model, f'models/bevel_classifier_{model_filename}.pkl')
    
    comparison_bevel[model_name] = {
        'accuracy': float(accuracy),
        'f1': float(f1),
        'auc': float(auc),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std())
    }
    
    if auc > best_auc_bevel:
        best_auc_bevel = auc
        best_model_bevel = (model_name, model)

# Save comparison
json.dump(comparison_bevel, open('models/bevel_model_comparison.json', 'w'), indent=2)

# Save best model as default
if best_model_bevel:
    joblib.dump(best_model_bevel[1], 'models/bevel_classifier.pkl')
    print(f"\n   ✅ Best: {best_model_bevel[0]} (AUC: {best_auc_bevel:.4f})")

# SHAP for best model
print(f"\n   Computing SHAP values...")
try:
    import shap
    ex_idx = np.random.default_rng(1).choice(len(X_bevel_scaled), min(500, len(X_bevel_scaled)), replace=False)
    X_explain_b = X_bevel_scaled[ex_idx]
    
    if 'Logistic' in best_model_bevel[0] or 'SVM' in best_model_bevel[0]:
        explainer_b = shap.LinearExplainer(best_model_bevel[1], X_bevel_scaled)
    else:
        explainer_b = shap.TreeExplainer(best_model_bevel[1])
    
    shap_values_b = explainer_b.shap_values(X_explain_b)
    
    joblib.dump({
        'explainer': explainer_b,
        'shap_values': shap_values_b,
        'X_sample': X_explain_b,
        'feature_names': BEVEL_FEATURES,
        'class_names': list(le_bevel.classes_),
        'model_name': best_model_bevel[0]
    }, 'xai/bevel_shap_artifacts.pkl')
    
    print(f"   ✅ SHAP artifacts saved")
except Exception as e:
    print(f"   ⚠️  SHAP failed: {e}")

print(f"\n✅ BEVEL GEAR TRAINING COMPLETE!")

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════

print(f"\n{'=' * 80}")
print("📊 TRAINING SUMMARY")
print(f"{'=' * 80}")

print(f"\nSPUR GEAR ({len(comparison_spur)} models):")
for model_name, metrics in sorted(comparison_spur.items(), key=lambda x: x[1]['auc'], reverse=True):
    print(f"   {model_name:25s} — Acc: {metrics['accuracy']:.4f}, AUC: {metrics['auc']:.4f}")

print(f"\nBEVEL GEAR ({len(comparison_bevel)} models):")
for model_name, metrics in sorted(comparison_bevel.items(), key=lambda x: x[1]['auc'], reverse=True):
    print(f"   {model_name:25s} — Acc: {metrics['accuracy']:.4f}, AUC: {metrics['auc']:.4f}")

print(f"\n{'=' * 80}")
print("✅ ALL TRAINING COMPLETE!")
print(f"{'=' * 80}")
print(f"\nTotal models trained: {len(comparison_spur) + len(comparison_bevel)}")
print(f"   Spur:  {len(comparison_spur)} models")
print(f"   Bevel: {len(comparison_bevel)} models")
print(f"\nNext steps:")
print(f"  1. Restart API: py -m uvicorn gear_api:app --reload --port 8000")
print(f"  2. Refresh dashboard to see all models")
print(f"  3. Test Model Comparison tab")
