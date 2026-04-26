"""
Efficient Spur Gear Model Training - Optimized for Performance
Target: >95% accuracy with minimal computational load

Key optimizations:
1. Fewer but more effective features
2. Optimized hyperparameters (not grid search)
3. Smaller ensemble sizes
4. Efficient algorithms
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.utils import resample
import xgboost as xgb
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("EFFICIENT SPUR GEAR MODEL TRAINING")
print("Target: >95% Accuracy | Optimized for Laptop Performance")
print("=" * 70)

# Load data
print("\n📊 Loading Spur Gear Dataset...")
df = pd.read_csv('../data/spur_gear_svm_dataset.csv')
print(f"   Dataset shape: {df.shape}")

# Check class distribution
print(f"\n   Original class distribution:")
print(df['Failure'].value_counts())

# Feature Engineering - Only most effective features
print("\n🔧 Creating Key Features...")

# Most impactful interaction features
df['Speed_Torque'] = df['Speed_RPM'] * df['Torque_Nm']
df['Vib_Temp'] = df['Vibration_mm_s'] * df['Temperature_C']
df['Shock_Noise'] = df['Shock_Load_g'] * df['Noise_dB']
df['Stress_Index'] = df['Vibration_mm_s'] * df['Shock_Load_g']

# Key squared features
df['Vib_Squared'] = df['Vibration_mm_s'] ** 2
df['Temp_Squared'] = df['Temperature_C'] ** 2

print(f"   Total features: {df.shape[1] - 1}")

# Separate features and target
X = df.drop('Failure', axis=1)
y = df['Failure']

# Balance the dataset
print("\n⚖️  Balancing Dataset...")
df_majority = df[df['Failure'] == 0]
df_minority = df[df['Failure'] == 1]

# Oversample minority class
df_minority_upsampled = resample(df_minority,
                                  replace=True,
                                  n_samples=len(df_majority),
                                  random_state=42)

df_balanced = pd.concat([df_majority, df_minority_upsampled])
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

X_balanced = df_balanced.drop('Failure', axis=1)
y_balanced = df_balanced['Failure']

print(f"   Balanced class distribution:")
print(y_balanced.value_counts())

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
)

print(f"\n   Train set: {X_train.shape}")
print(f"   Test set: {X_test.shape}")

# Scale features
print("\n📏 Scaling Features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# For RUL prediction
scaler_rul = StandardScaler()
X_train_rul = scaler_rul.fit_transform(X_train[['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 
                                                  'Temperature_C', 'Shock_Load_g', 'Noise_dB']])
X_test_rul = scaler_rul.transform(X_test[['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 
                                           'Temperature_C', 'Shock_Load_g', 'Noise_dB']])

# Generate RUL values
y_rul_train = np.where(y_train == 1, 
                       np.random.randint(100, 1000, size=len(y_train)),
                       np.random.randint(5000, 15000, size=len(y_train)))
y_rul_test = np.where(y_test == 1,
                      np.random.randint(100, 1000, size=len(y_test)),
                      np.random.randint(5000, 15000, size=len(y_test)))

# Dictionary to store results
results = {}

print("\n" + "=" * 70)
print("TRAINING 5 OPTIMIZED MODELS")
print("=" * 70)

# 1. Logistic Regression - Fast and efficient
print("\n1️⃣  Training Logistic Regression...")
lr_model = LogisticRegression(
    C=0.5,
    max_iter=1000,
    solver='lbfgs',
    class_weight='balanced',
    random_state=42
)
lr_model.fit(X_train_scaled, y_train)
lr_pred = lr_model.predict(X_test_scaled)
lr_proba = lr_model.predict_proba(X_test_scaled)

lr_acc = accuracy_score(y_test, lr_pred)
lr_f1 = f1_score(y_test, lr_pred, average='weighted')
lr_auc = roc_auc_score(y_test, lr_proba[:, 1])
lr_cv = cross_val_score(lr_model, X_train_scaled, y_train, cv=3, scoring='accuracy')

results['Logistic Regression'] = {
    'accuracy': float(lr_acc),
    'f1': float(lr_f1),
    'auc': float(lr_auc),
    'cv_mean': float(lr_cv.mean()),
    'cv_std': float(lr_cv.std())
}

print(f"   ✅ Accuracy: {lr_acc*100:.2f}%")
print(f"   ✅ AUC: {lr_auc*100:.2f}%")

# 2. Random Forest - Moderate size for efficiency
print("\n2️⃣  Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,  # Reduced from 300
    max_depth=15,      # Reduced from 20
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
rf_pred = rf_model.predict(X_test_scaled)
rf_proba = rf_model.predict_proba(X_test_scaled)

rf_acc = accuracy_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred, average='weighted')
rf_auc = roc_auc_score(y_test, rf_proba[:, 1])
rf_cv = cross_val_score(rf_model, X_train_scaled, y_train, cv=3, scoring='accuracy')

results['Random Forest'] = {
    'accuracy': float(rf_acc),
    'f1': float(rf_f1),
    'auc': float(rf_auc),
    'cv_mean': float(rf_cv.mean()),
    'cv_std': float(rf_cv.std())
}

print(f"   ✅ Accuracy: {rf_acc*100:.2f}%")
print(f"   ✅ AUC: {rf_auc*100:.2f}%")

# 3. Gradient Boosting - Optimized size
print("\n3️⃣  Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,  # Reduced from 200
    learning_rate=0.1,
    max_depth=5,       # Reduced from 7
    min_samples_split=5,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
gb_pred = gb_model.predict(X_test_scaled)
gb_proba = gb_model.predict_proba(X_test_scaled)

gb_acc = accuracy_score(y_test, gb_pred)
gb_f1 = f1_score(y_test, gb_pred, average='weighted')
gb_auc = roc_auc_score(y_test, gb_proba[:, 1])
gb_cv = cross_val_score(gb_model, X_train_scaled, y_train, cv=3, scoring='accuracy')

results['Gradient Boosting'] = {
    'accuracy': float(gb_acc),
    'f1': float(gb_f1),
    'auc': float(gb_auc),
    'cv_mean': float(gb_cv.mean()),
    'cv_std': float(gb_cv.std())
}

print(f"   ✅ Accuracy: {gb_acc*100:.2f}%")
print(f"   ✅ AUC: {gb_auc*100:.2f}%")

# 4. SVM - Efficient with RBF kernel
print("\n4️⃣  Training SVM (RBF)...")
svm_model = SVC(
    C=5,  # Moderate regularization
    gamma='scale',
    kernel='rbf',
    class_weight='balanced',
    probability=True,
    random_state=42
)
svm_model.fit(X_train_scaled, y_train)
svm_pred = svm_model.predict(X_test_scaled)
svm_proba = svm_model.predict_proba(X_test_scaled)

svm_acc = accuracy_score(y_test, svm_pred)
svm_f1 = f1_score(y_test, svm_pred, average='weighted')
svm_auc = roc_auc_score(y_test, svm_proba[:, 1])
svm_cv = cross_val_score(svm_model, X_train_scaled, y_train, cv=3, scoring='accuracy')

results['SVM (RBF)'] = {
    'accuracy': float(svm_acc),
    'f1': float(svm_f1),
    'auc': float(svm_auc),
    'cv_mean': float(svm_cv.mean()),
    'cv_std': float(svm_cv.std())
}

print(f"   ✅ Accuracy: {svm_acc*100:.2f}%")
print(f"   ✅ AUC: {svm_auc*100:.2f}%")

# 5. XGBoost - Optimized for speed
print("\n5️⃣  Training XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=100,  # Reduced from 200
    learning_rate=0.1,
    max_depth=5,       # Reduced from 7
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss',
    n_jobs=-1
)
xgb_model.fit(X_train_scaled, y_train)
xgb_pred = xgb_model.predict(X_test_scaled)
xgb_proba = xgb_model.predict_proba(X_test_scaled)

xgb_acc = accuracy_score(y_test, xgb_pred)
xgb_f1 = f1_score(y_test, xgb_pred, average='weighted')
xgb_auc = roc_auc_score(y_test, xgb_proba[:, 1])
xgb_cv = cross_val_score(xgb_model, X_train_scaled, y_train, cv=3, scoring='accuracy')

results['XGBoost'] = {
    'accuracy': float(xgb_acc),
    'f1': float(xgb_f1),
    'auc': float(xgb_auc),
    'cv_mean': float(xgb_cv.mean()),
    'cv_std': float(xgb_cv.std())
}

print(f"   ✅ Accuracy: {xgb_acc*100:.2f}%")
print(f"   ✅ AUC: {xgb_auc*100:.2f}%")

# Find best model
best_model_name = max(results, key=lambda k: results[k]['accuracy'])
best_model = {
    'Logistic Regression': lr_model,
    'Random Forest': rf_model,
    'Gradient Boosting': gb_model,
    'SVM (RBF)': svm_model,
    'XGBoost': xgb_model
}[best_model_name]

print("\n" + "=" * 70)
print(f"🏆 BEST MODEL: {best_model_name}")
print(f"   Accuracy: {results[best_model_name]['accuracy']*100:.2f}%")
print(f"   AUC: {results[best_model_name]['auc']*100:.2f}%")
print("=" * 70)

# Train RUL regressor - Lightweight
print("\n📈 Training RUL Regressor...")
from sklearn.ensemble import RandomForestRegressor

rul_model = RandomForestRegressor(
    n_estimators=50,  # Reduced for efficiency
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
rul_model.fit(X_train_rul, y_rul_train)
rul_pred = rul_model.predict(X_test_rul)
rul_score = rul_model.score(X_test_rul, y_rul_test)

print(f"   ✅ RUL R² Score: {rul_score:.4f}")

# Save all models
print("\n💾 Saving Models...")
joblib.dump(lr_model, 'spur_classifier_lr.pkl')
joblib.dump(rf_model, 'spur_classifier_rf.pkl')
joblib.dump(gb_model, 'spur_classifier_gb.pkl')
joblib.dump(svm_model, 'spur_classifier_svm.pkl')
joblib.dump(xgb_model, 'spur_classifier_xgb.pkl')
joblib.dump(rul_model, 'spur_rul_regressor.pkl')
joblib.dump(scaler, 'spur_scaler.pkl')
joblib.dump(scaler_rul, 'spur_scaler_rul.pkl')

# Create label encoder
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(['No Failure', 'Failure'])
joblib.dump(le, 'spur_label_encoder.pkl')

print("   ✅ All models saved")

# Save comparison results
with open('spur_model_comparison.json', 'w') as f:
    json.dump(results, f, indent=2)
print("   ✅ Comparison results saved")

# Create SHAP explainer - Lightweight version
print("\n🔍 Creating SHAP Explainer...")
try:
    import shap
    # Use smaller sample for SHAP
    X_sample = X_train_scaled[:100]  # Reduced from 300
    
    if best_model_name in ['Random Forest', 'Gradient Boosting', 'XGBoost']:
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(X_sample)
    else:
        explainer = shap.LinearExplainer(best_model, X_sample)
        shap_values = explainer.shap_values(X_sample)
    
    shap_artifacts = {
        'explainer': explainer,
        'X_sample': X_sample,
        'feature_names': list(X_train.columns),
        'model': best_model
    }
    
    joblib.dump(shap_artifacts, '../xai/spur_shap_artifacts.pkl')
    print("   ✅ SHAP artifacts saved")
except Exception as e:
    print(f"   ⚠️  SHAP creation skipped: {e}")

# Print final summary
print("\n" + "=" * 70)
print("TRAINING COMPLETE - SUMMARY")
print("=" * 70)
print("\nModel Performance (sorted by accuracy):")
for model_name, metrics in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
    print(f"\n{model_name}:")
    print(f"  Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"  F1 Score: {metrics['f1']*100:.2f}%")
    print(f"  AUC: {metrics['auc']*100:.2f}%")
    print(f"  CV Mean: {metrics['cv_mean']*100:.2f}% (±{metrics['cv_std']*100:.2f}%)")

# Check if target achieved
target_achieved = any(m['accuracy'] >= 0.95 for m in results.values())
print("\n" + "=" * 70)
if target_achieved:
    print("✅ TARGET ACHIEVED: At least one model has >95% accuracy!")
else:
    print("⚠️  Target not fully achieved. Best: {:.2f}%".format(max(m['accuracy'] for m in results.values())*100))
    print("   Consider: More data, different features, or ensemble methods")
print("=" * 70)
