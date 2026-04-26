"""
Retrain Spur Gear Models with Fixed AUC Calculation
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
print("🔧 RETRAINING SPUR GEAR - FIXED AUC CALCULATION")
print("=" * 80)

# Load dataset
df_spur = pd.read_csv('data/spur_gear_svm_dataset.csv')
print(f"   Full dataset: {len(df_spur)} rows")

# Sample for faster training
SAMPLE_SIZE = 20000
df_spur_sample = df_spur.groupby('Failure', group_keys=False).apply(
    lambda x: x.sample(min(len(x), SAMPLE_SIZE//2), random_state=42)
).reset_index(drop=True)
print(f"   Using sample: {len(df_spur_sample)} rows")

SPUR_FEATURES = ['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 'Temperature_C', 'Shock_Load_g', 'Noise_dB']
X_spur = df_spur_sample[SPUR_FEATURES].values

# Create 3-class labels for better classification
def create_spur_labels_3class(df):
    """Create 3-class labels: No Failure, Minor Failure, Major Failure"""
    labels = []
    for _, row in df.iterrows():
        if row['Failure'] == 0:
            labels.append('No Failure')
        else:
            # Use multiple sensors to determine severity
            severity_score = 0
            if row['Vibration_mm_s'] > 12:
                severity_score += 2
            elif row['Vibration_mm_s'] > 8:
                severity_score += 1
            
            if row['Temperature_C'] > 95:
                severity_score += 2
            elif row['Temperature_C'] > 85:
                severity_score += 1
            
            if row['Noise_dB'] > 85:
                severity_score += 1
            
            if severity_score >= 3:
                labels.append('Major Failure')
            else:
                labels.append('Minor Failure')
    return np.array(labels)

y_spur_labels = create_spur_labels_3class(df_spur_sample)
le_spur = LabelEncoder()
y_spur = le_spur.fit_transform(y_spur_labels)

print(f"   Classes: {list(le_spur.classes_)}")
for cls in le_spur.classes_:
    count = np.sum(y_spur_labels == cls)
    print(f"      {cls}: {count} ({count/len(y_spur)*100:.1f}%)")

# Scale
scaler_spur = StandardScaler()
X_spur_scaled = scaler_spur.fit_transform(X_spur)

# Split
X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X_spur_scaled, y_spur, test_size=0.2, random_state=42, stratify=y_spur
)

# RUL
print(f"\n   Training RUL Regressor...")
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

# Define models
def get_models():
    models = {
        'Logistic Regression': LogisticRegression(
            multi_class='multinomial', solver='lbfgs', C=1.0,
            max_iter=500, random_state=42, class_weight='balanced'
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=10,
            random_state=42, class_weight='balanced', n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42
        ),
        'SVM (RBF)': SVC(
            kernel='rbf', C=5.0, gamma='scale',
            probability=True, random_state=42, max_iter=1000, class_weight='balanced'
        )
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = xgb.XGBClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42, eval_metric='mlogloss', use_label_encoder=False,
            n_jobs=-1
        )
    
    return models

# Train models
models_spur = get_models()
comparison_spur = {}
best_model_spur = None
best_auc_spur = 0.0

print(f"\n   Training 5 models...")

for model_name, model in models_spur.items():
    print(f"\n   {model_name}...", end=' ')
    
    model.fit(X_train_s, y_train_s)
    y_pred_s = model.predict(X_test_s)
    y_proba_s = model.predict_proba(X_test_s)
    
    accuracy = accuracy_score(y_test_s, y_pred_s)
    f1 = f1_score(y_test_s, y_pred_s, average='weighted')
    
    # Calculate AUC properly for multi-class
    try:
        if len(le_spur.classes_) == 2:
            auc = roc_auc_score(y_test_s, y_proba_s[:, 1])
        else:
            # Multi-class AUC (one-vs-rest)
            y_test_bin = label_binarize(y_test_s, classes=range(len(le_spur.classes_)))
            auc = roc_auc_score(y_test_bin, y_proba_s, average='weighted', multi_class='ovr')
    except Exception as e:
        print(f"AUC Error: {e}")
        auc = 0.0
    
    cv_scores = cross_val_score(model, X_spur_scaled, y_spur, cv=3, scoring='accuracy')
    
    print(f"Acc: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")
    
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

if best_model_spur:
    joblib.dump(best_model_spur[1], 'models/spur_classifier.pkl')
    print(f"\n   ✅ Best: {best_model_spur[0]} (AUC: {best_auc_spur:.4f})")
else:
    print(f"\n   ⚠️  Using first model as default")
    first_model = list(models_spur.items())[0]
    joblib.dump(first_model[1], 'models/spur_classifier.pkl')

# SHAP
try:
    import shap
    print(f"\n   Computing SHAP...", end=' ')
    ex_idx = np.random.choice(len(X_spur_scaled), min(300, len(X_spur_scaled)), replace=False)
    X_explain_s = X_spur_scaled[ex_idx]
    
    if best_model_spur and ('Logistic' in best_model_spur[0] or 'SVM' in best_model_spur[0]):
        explainer_s = shap.LinearExplainer(best_model_spur[1], X_spur_scaled)
    elif best_model_spur:
        explainer_s = shap.TreeExplainer(best_model_spur[1])
    else:
        explainer_s = shap.TreeExplainer(list(models_spur.values())[0])
    
    shap_values_s = explainer_s.shap_values(X_explain_s)
    
    os.makedirs('xai', exist_ok=True)
    joblib.dump({
        'explainer': explainer_s,
        'shap_values': shap_values_s,
        'X_sample': X_explain_s,
        'feature_names': SPUR_FEATURES,
        'class_names': list(le_spur.classes_),
        'model_name': best_model_spur[0] if best_model_spur else 'Random Forest'
    }, 'xai/spur_shap_artifacts.pkl')
    print("Done")
except Exception as e:
    print(f"Failed: {e}")

print(f"\n{'=' * 80}")
print("✅ SPUR GEAR RETRAINING COMPLETE!")
print(f"{'=' * 80}")

print(f"\nModels trained:")
for name, m in sorted(comparison_spur.items(), key=lambda x: x[1]['auc'], reverse=True):
    print(f"   {name:25s} Acc: {m['accuracy']:.4f}, AUC: {m['auc']:.4f}")

print(f"\nRestart API to load updated models:")
print(f"  py -m uvicorn gear_api:app --reload --port 8000")
