"""
Optimized Training for Spur and Bevel - 5 Models Each
Uses data sampling for faster training while maintaining accuracy
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
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except:
    HAS_XGBOOST = False

print("=" * 80)
print("🚀 OPTIMIZED TRAINING - SPUR AND BEVEL GEARS")
print("=" * 80)

def get_models_optimized():
    """Return optimized models for faster training."""
    models = {
        'Logistic Regression': LogisticRegression(
            multi_class='multinomial', solver='lbfgs', C=1.0,
            max_iter=500, random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=10,
            random_state=42, n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42
        ),
        'SVM (RBF)': SVC(
            kernel='rbf', C=5.0, gamma='scale',
            probability=True, random_state=42, max_iter=1000
        )
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = xgb.XGBClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42, eval_metric='logloss', use_label_encoder=False,
            n_jobs=-1
        )
    
    return models

# ═══════════════════════════════════════════════════════════
# TRAIN SPUR GEAR
# ═══════════════════════════════════════════════════════════

print(f"\n{'=' * 80}")
print("🔧 SPUR GEAR - 5 MODELS")
print(f"{'=' * 80}")

df_spur = pd.read_csv('data/spur_gear_svm_dataset.csv')
print(f"   Full dataset: {len(df_spur)} rows")

# Sample for faster training (stratified)
SAMPLE_SIZE = 20000
df_spur_sample = df_spur.groupby('Failure', group_keys=False).apply(
    lambda x: x.sample(min(len(x), SAMPLE_SIZE//2), random_state=42)
).reset_index(drop=True)
print(f"   Using sample: {len(df_spur_sample)} rows")

SPUR_FEATURES = ['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 'Temperature_C', 'Shock_Load_g', 'Noise_dB']
X_spur = df_spur_sample[SPUR_FEATURES].values

# Create 3-class labels
def create_spur_labels(df):
    labels = []
    for _, row in df.iterrows():
        if row['Failure'] == 0:
            labels.append('No Failure')
        else:
            if row['Vibration_mm_s'] > 12 or row['Temperature_C'] > 95:
                labels.append('Major Failure')
            else:
                labels.append('Minor Failure')
    return np.array(labels)

y_spur_labels = create_spur_labels(df_spur_sample)
le_spur = LabelEncoder()
y_spur = le_spur.fit_transform(y_spur_labels)
print(f"   Classes: {list(le_spur.classes_)}")

# Scale
scaler_spur = StandardScaler()
X_spur_scaled = scaler_spur.fit_transform(X_spur)

# Split
X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X_spur_scaled, y_spur, test_size=0.2, random_state=42, stratify=y_spur
)

# RUL
print(f"   Training RUL...")
rul_spur = np.where(y_spur_labels == 'No Failure', np.random.randint(40000, 80000, len(y_spur_labels)),
                    np.where(y_spur_labels == 'Minor Failure', np.random.randint(10000, 40000, len(y_spur_labels)),
                            np.random.randint(1000, 10000, len(y_spur_labels))))

scaler_rul_spur = StandardScaler()
X_rul_spur_scaled = scaler_rul_spur.fit_transform(X_spur)
rul_regressor_spur = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
rul_regressor_spur.fit(X_rul_spur_scaled, rul_spur)
print(f"   RUL R²: {rul_regressor_spur.score(X_rul_spur_scaled, rul_spur):.4f}")

# Save preprocessing
os.makedirs('models', exist_ok=True)
joblib.dump(scaler_spur, 'models/spur_scaler.pkl')
joblib.dump(le_spur, 'models/spur_label_encoder.pkl')
joblib.dump(rul_regressor_spur, 'models/spur_rul_regressor.pkl')
joblib.dump(scaler_rul_spur, 'models/spur_scaler_rul.pkl')

# Train models
models_spur = get_models_optimized()
comparison_spur = {}
best_model_spur = None
best_auc_spur = 0.0

for model_name, model in models_spur.items():
    print(f"\n   {model_name}...", end=' ')
    
    model.fit(X_train_s, y_train_s)
    y_pred_s = model.predict(X_test_s)
    y_proba_s = model.predict_proba(X_test_s)
    
    accuracy = accuracy_score(y_test_s, y_pred_s)
    f1 = f1_score(y_test_s, y_pred_s, average='weighted')
    
    try:
        if len(le_spur.classes_) == 2:
            # Binary classification - use simpler AUC
            auc = roc_auc_score(y_test_s, y_proba_s[:, 1])
        else:
            y_test_bin = label_binarize(y_test_s, classes=range(len(le_spur.classes_)))
            auc = roc_auc_score(y_test_bin, y_proba_s, average='weighted', multi_class='ovr')
    except:
        auc = 0.0
    
    cv_scores = cross_val_score(model, X_spur_scaled, y_spur, cv=3, scoring='accuracy')
    
    print(f"Acc: {accuracy:.4f}, AUC: {auc:.4f}")
    
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

json.dump(comparison_spur, open('models/spur_model_comparison.json', 'w'), indent=2)
if best_model_spur:
    joblib.dump(best_model_spur[1], 'models/spur_classifier.pkl')
    print(f"\n   ✅ Best: {best_model_spur[0]} (AUC: {best_auc_spur:.4f})")
else:
    print(f"\n   ⚠️  No best model found, using first model")
    first_model = list(models_spur.items())[0]
    joblib.dump(first_model[1], 'models/spur_classifier.pkl')
    best_model_spur = first_model

# SHAP
try:
    import shap
    print(f"   Computing SHAP...", end=' ')
    ex_idx = np.random.choice(len(X_spur_scaled), min(300, len(X_spur_scaled)), replace=False)
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
    print("Done")
except Exception as e:
    print(f"Failed: {e}")

# ═══════════════════════════════════════════════════════════
# TRAIN BEVEL GEAR
# ═══════════════════════════════════════════════════════════

print(f"\n{'=' * 80}")
print("🔩 BEVEL GEAR - 5 MODELS")
print(f"{'=' * 80}")

df_bevel = pd.read_csv('data/bevel_rul_dataset.csv')
print(f"   Full dataset: {len(df_bevel)} rows")

# Sample for faster training
df_bevel_sample = df_bevel.sample(min(20000, len(df_bevel)), random_state=42)
print(f"   Using sample: {len(df_bevel_sample)} rows")

BEVEL_FEATURES = ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)', 
                  'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use']
X_bevel = df_bevel_sample[BEVEL_FEATURES].values
rul_bevel = df_bevel_sample['RUL (cycles)'].values

# Create labels from RUL
y_bevel_labels = np.where(rul_bevel > 50000, 'No Fault',
                          np.where(rul_bevel > 20000, 'Minor Fault', 'Major Fault'))

le_bevel = LabelEncoder()
y_bevel = le_bevel.fit_transform(y_bevel_labels)
print(f"   Classes: {list(le_bevel.classes_)}")

# Scale
scaler_bevel = StandardScaler()
X_bevel_scaled = scaler_bevel.fit_transform(X_bevel)

# Split
X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X_bevel_scaled, y_bevel, test_size=0.2, random_state=42, stratify=y_bevel
)

# RUL
print(f"   Training RUL...")
scaler_rul_bevel = StandardScaler()
X_rul_bevel_scaled = scaler_rul_bevel.fit_transform(X_bevel)
rul_regressor_bevel = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
rul_regressor_bevel.fit(X_rul_bevel_scaled, rul_bevel)
print(f"   RUL R²: {rul_regressor_bevel.score(X_rul_bevel_scaled, rul_bevel):.4f}")

# Save preprocessing
joblib.dump(scaler_bevel, 'models/bevel_scaler.pkl')
joblib.dump(le_bevel, 'models/bevel_label_encoder.pkl')
joblib.dump(rul_regressor_bevel, 'models/bevel_rul_regressor.pkl')
joblib.dump(scaler_rul_bevel, 'models/bevel_scaler_rul.pkl')

# Train models
models_bevel = get_models_optimized()
comparison_bevel = {}
best_model_bevel = None
best_auc_bevel = 0.0

for model_name, model in models_bevel.items():
    print(f"\n   {model_name}...", end=' ')
    
    model.fit(X_train_b, y_train_b)
    y_pred_b = model.predict(X_test_b)
    y_proba_b = model.predict_proba(X_test_b)
    
    accuracy = accuracy_score(y_test_b, y_pred_b)
    f1 = f1_score(y_test_b, y_pred_b, average='weighted')
    
    try:
        if len(le_bevel.classes_) == 2:
            auc = roc_auc_score(y_test_b, y_proba_b[:, 1])
        else:
            y_test_bin = label_binarize(y_test_b, classes=range(len(le_bevel.classes_)))
            auc = roc_auc_score(y_test_bin, y_proba_b, average='weighted', multi_class='ovr')
    except:
        auc = 0.0
    
    cv_scores = cross_val_score(model, X_bevel_scaled, y_bevel, cv=3, scoring='accuracy')
    
    print(f"Acc: {accuracy:.4f}, AUC: {auc:.4f}")
    
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

json.dump(comparison_bevel, open('models/bevel_model_comparison.json', 'w'), indent=2)
if best_model_bevel:
    joblib.dump(best_model_bevel[1], 'models/bevel_classifier.pkl')
    print(f"\n   ✅ Best: {best_model_bevel[0]} (AUC: {best_auc_bevel:.4f})")
else:
    print(f"\n   ⚠️  No best model found, using first model")
    first_model = list(models_bevel.items())[0]
    joblib.dump(first_model[1], 'models/bevel_classifier.pkl')
    best_model_bevel = first_model

# SHAP
try:
    import shap
    print(f"   Computing SHAP...", end=' ')
    ex_idx = np.random.choice(len(X_bevel_scaled), min(300, len(X_bevel_scaled)), replace=False)
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
    print("Done")
except Exception as e:
    print(f"Failed: {e}")

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════

print(f"\n{'=' * 80}")
print("📊 SUMMARY")
print(f"{'=' * 80}")

print(f"\nSPUR ({len(comparison_spur)} models):")
for name, m in sorted(comparison_spur.items(), key=lambda x: x[1]['auc'], reverse=True):
    print(f"   {name:25s} Acc: {m['accuracy']:.4f}, AUC: {m['auc']:.4f}")

print(f"\nBEVEL ({len(comparison_bevel)} models):")
for name, m in sorted(comparison_bevel.items(), key=lambda x: x[1]['auc'], reverse=True):
    print(f"   {name:25s} Acc: {m['accuracy']:.4f}, AUC: {m['auc']:.4f}")

print(f"\n{'=' * 80}")
print("✅ TRAINING COMPLETE!")
print(f"{'=' * 80}")
print(f"\nTotal: {len(comparison_spur) + len(comparison_bevel)} models")
print(f"\nRestart API to load new models:")
print(f"  py -m uvicorn gear_api:app --reload --port 8000")
