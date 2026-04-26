"""
═══════════════════════════════════════════════════════════
MODULE 2 — ML PIPELINE
GearMind AI · Elecon Engineering Works Pvt. Ltd.
═══════════════════════════════════════════════════════════

WHAT THIS FILE DOES:
  1. Loads the physics-based dataset from Module 1
  2. Handles class imbalance with SMOTE
  3. Trains and compares 5 ML models
  4. Picks the best model automatically
  5. Trains a separate RUL regression model
  6. Tracks all experiments with MLflow
  7. Saves trained models for the dashboard

HOW TO RUN:
  pip install scikit-learn xgboost imbalanced-learn mlflow joblib
  python models/train_models.py

OUTPUT:
  models/best_classifier.pkl   → best fault classification model
  models/rul_regressor.pkl     → RUL prediction model
  models/scaler.pkl            → feature scaler
  models/label_encoder.pkl     → label encoder
  mlruns/                      → MLflow experiment logs
"""

import pandas as pd
import numpy as np
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                              classification_report, confusion_matrix)
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import mlflow
import mlflow.sklearn

print("🤖 GearMind ML Pipeline Starting...")

# ════════════════════════════════════════════════════════
# STEP 1: Load Data
# ════════════════════════════════════════════════════════

df = pd.read_csv('data/helical_gear_dataset.csv')
print(f"   ✅ Loaded {len(df):,} samples")

# Feature columns — the 8 sensor readings
FEATURE_COLS = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]
TARGET_COL = 'Fault Label'

X = df[FEATURE_COLS].values
y_raw = df[TARGET_COL].values

# ════════════════════════════════════════════════════════
# STEP 2: Encode Labels
# ════════════════════════════════════════════════════════

le = LabelEncoder()
y = le.fit_transform(y_raw)
# Classes: 0=Major Fault, 1=Minor Fault, 2=No Fault (alphabetical)
print(f"   ✅ Classes: {list(le.classes_)}")

# ════════════════════════════════════════════════════════
# STEP 3: Train/Test Split
# ════════════════════════════════════════════════════════

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y          # ensures same class ratio in train and test
)
print(f"   ✅ Train: {len(X_train):,} | Test: {len(X_test):,}")

# ════════════════════════════════════════════════════════
# STEP 4: Feature Scaling
# ════════════════════════════════════════════════════════
# StandardScaler: makes all features have mean=0, std=1
# Important for models like Logistic Regression and SVM

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)   # fit on train only!
X_test_sc  = scaler.transform(X_test)         # just transform test

# ════════════════════════════════════════════════════════
# STEP 5: Handle Class Imbalance with SMOTE
# ════════════════════════════════════════════════════════
# Real fault data is imbalanced — faults are rare!
# SMOTE creates synthetic minority class samples

print("\n   Applying SMOTE for class imbalance...")
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train_sc, y_train)
print(f"   ✅ Before SMOTE: {len(X_train_sc):,} | After SMOTE: {len(X_train_bal):,}")

# ════════════════════════════════════════════════════════
# STEP 6: Define 5 Models to Compare
# ════════════════════════════════════════════════════════

models = {
    # Simple baseline — good for comparison
    'Logistic Regression': LogisticRegression(
        max_iter=1000, random_state=42
    ),
    
    # Ensemble of decision trees — usually very good
    'Random Forest': RandomForestClassifier(
        n_estimators=200, max_depth=8,
        random_state=42, n_jobs=-1
    ),
    
    # Boosting — builds trees sequentially fixing errors
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1,
        max_depth=4, subsample=0.8, random_state=42
    ),
    
    # XGBoost — faster and often better than GBM
    'XGBoost': xgb.XGBClassifier(
        n_estimators=100, learning_rate=0.1,
        max_depth=5, subsample=0.8,
        eval_metric='mlogloss',
        random_state=42, n_jobs=-1
    ),
    
    # SVM with linear kernel (much faster than rbf)
    'SVM': SVC(
        kernel='linear', C=1,
        probability=True, random_state=42
    ),
}

# ════════════════════════════════════════════════════════
# STEP 7: Train, Evaluate & Track with MLflow
# ════════════════════════════════════════════════════════

mlflow.set_experiment("GearMind_Fault_Classification")

results = {}
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\n" + "═"*60)
print("🏋️  TRAINING 5 MODELS — CROSS VALIDATION")
print("═"*60)

for model_name, model in models.items():
    print(f"\n   [{model_name}]")
    
    with mlflow.start_run(run_name=model_name):
        
        # 5-Fold Cross Validation on training data
        # Gives mean ± std accuracy — more reliable than single split
        cv_scores = cross_val_score(
            model, X_train_bal, y_train_bal,
            cv=kfold, scoring='accuracy', n_jobs=-1
        )
        
        # Train on full balanced training set
        model.fit(X_train_bal, y_train_bal)
        
        # Evaluate on held-out test set
        y_pred      = model.predict(X_test_sc)
        y_pred_prob = model.predict_proba(X_test_sc)
        
        # Calculate metrics
        acc     = accuracy_score(y_test, y_pred)
        f1      = f1_score(y_test, y_pred, average='weighted')
        auc     = roc_auc_score(y_test, y_pred_prob, multi_class='ovr')
        cv_mean = cv_scores.mean()
        cv_std  = cv_scores.std()
        
        # Log to MLflow
        mlflow.log_params({
            "model_type": model_name,
            "smote": True,
            "n_features": len(FEATURE_COLS),
            "train_samples": len(X_train_bal),
        })
        mlflow.log_metrics({
            "accuracy":   acc,
            "f1_score":   f1,
            "roc_auc":    auc,
            "cv_mean":    cv_mean,
            "cv_std":     cv_std,
        })
        mlflow.sklearn.log_model(model, model_name)
        
        results[model_name] = {
            'model':    model,
            'accuracy': acc,
            'f1':       f1,
            'auc':      auc,
            'cv_mean':  cv_mean,
            'cv_std':   cv_std,
        }
        
        print(f"   CV Accuracy:  {cv_mean:.4f} ± {cv_std:.4f}")
        print(f"   Test Accuracy:{acc:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")

# ════════════════════════════════════════════════════════
# STEP 8: Print Comparison Table & Pick Best Model
# ════════════════════════════════════════════════════════

print("\n" + "═"*70)
print("📊 MODEL COMPARISON TABLE")
print("═"*70)
print(f"{'Model':<22} {'CV Acc':>8} {'Test Acc':>10} {'F1':>8} {'AUC':>8}")
print("─"*70)

best_model_name = None
best_auc = 0

for name, r in results.items():
    print(f"{name:<22} {r['cv_mean']:>8.4f} {r['accuracy']:>10.4f} {r['f1']:>8.4f} {r['auc']:>8.4f}")
    if r['auc'] > best_auc:
        best_auc = r['auc']
        best_model_name = name

print("─"*70)
print(f"\n🏆 Best Model: {best_model_name} (AUC: {best_auc:.4f})")
best_model = results[best_model_name]['model']

# Full classification report for best model
y_pred_best = best_model.predict(X_test_sc)
print(f"\n📋 Classification Report — {best_model_name}:")
print(classification_report(y_test, y_pred_best, target_names=le.classes_))

# ════════════════════════════════════════════════════════
# STEP 9: Train RUL Regression Model
# ════════════════════════════════════════════════════════

print("\n" + "═"*60)
print("⏱  TRAINING RUL REGRESSION MODEL")
print("═"*60)

rul_df = pd.read_csv('data/rul_dataset.csv')
X_rul = rul_df[FEATURE_COLS].values
y_rul = rul_df['RUL (cycles)'].values

X_rul_train, X_rul_test, y_rul_train, y_rul_test = train_test_split(
    X_rul, y_rul, test_size=0.2, random_state=42
)

# Scale for regression too
scaler_rul = StandardScaler()
X_rul_train_sc = scaler_rul.fit_transform(X_rul_train)
X_rul_test_sc  = scaler_rul.transform(X_rul_test)

# Random Forest Regressor for RUL
rul_model = RandomForestRegressor(
    n_estimators=200, max_depth=10,
    random_state=42, n_jobs=-1
)
rul_model.fit(X_rul_train_sc, y_rul_train)

y_rul_pred = rul_model.predict(X_rul_test_sc)
rul_mae  = np.mean(np.abs(y_rul_test - y_rul_pred))
rul_r2   = 1 - np.sum((y_rul_test - y_rul_pred)**2) / np.sum((y_rul_test - y_rul_pred.mean())**2)

print(f"   ✅ RUL Model — MAE: {rul_mae:,.0f} cycles | R²: {rul_r2:.4f}")

# Log RUL model to MLflow
with mlflow.start_run(run_name="RUL_Regressor"):
    mlflow.log_metrics({"mae": rul_mae, "r2": rul_r2})
    mlflow.sklearn.log_model(rul_model, "RUL_RandomForest")

# ════════════════════════════════════════════════════════
# STEP 10: Save All Model Artifacts
# ════════════════════════════════════════════════════════

os.makedirs('models', exist_ok=True)

joblib.dump(best_model,  'models/best_classifier.pkl')
joblib.dump(rul_model,   'models/rul_regressor.pkl')
joblib.dump(scaler,      'models/scaler.pkl')
joblib.dump(scaler_rul,  'models/scaler_rul.pkl')
joblib.dump(le,          'models/label_encoder.pkl')

# Save results summary for dashboard
results_summary = {
    name: {k: v for k, v in r.items() if k != 'model'}
    for name, r in results.items()
}
import json
with open('models/model_comparison.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

print("\n✅ Saved:")
print("   models/best_classifier.pkl")
print("   models/rul_regressor.pkl")
print("   models/scaler.pkl")
print("   models/label_encoder.pkl")
print("   models/model_comparison.json")
print("\n🚀 Run next: python xai/explain.py")
print("📊 View MLflow: mlflow ui  (then open http://localhost:5000)")
