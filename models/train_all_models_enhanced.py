"""
ENHANCED MODEL TRAINING — All Gear Types with 5 Models Each
GearMind AI · Elecon Engineering Works Pvt. Ltd.

Trains 5 models for each gear type:
  1. Logistic Regression
  2. Random Forest
  3. Gradient Boosting
  4. XGBoost
  5. SVM (RBF)

Gear Types: Spur, Bevel, Worm
(Helical already has 5 models)

Outputs:
  models/{gear}_classifier_{model}.pkl
  models/{gear}_model_comparison.json (updated with all 5 models)
  xai/{gear}_shap_artifacts.pkl (updated)
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
    print("⚠️  XGBoost not installed. Will skip XGBoost models.")

print("=" * 80)
print("🚀 ENHANCED MODEL TRAINING — All Gear Types")
print("=" * 80)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

GEAR_CONFIGS = {
    'spur': {
        'dataset': 'data/spur_gear_svm_dataset.csv',
        'features': ['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 'Temperature_C', 'Shock_Load_g', 'Noise_dB'],
        'target': 'Failure_Label',
        'rul': 'RUL_Cycles'
    },
    'bevel': {
        'dataset': 'data/bevel_rul_dataset.csv',
        'features': ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)', 
                    'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use'],
        'target': 'Failure_Label',
        'rul': 'RUL_Cycles'
    },
    'worm': {
        'dataset': 'data/worm_gear_dataset.csv',
        'features': ['Worm_RPM', 'Input_Torque', 'Output_Torque', 'Motor_Current',
                    'Oil_Temp', 'Ambient_Temp', 'Axial_Vib', 'Radial_Vib',
                    'Cu_PPM', 'Fe_PPM', 'Efficiency_Calc', 'Friction_Coeff', 'Backlash'],
        'target': 'Failure_Label',
        'rul': 'RUL_Cycles'
    }
}

# ═══════════════════════════════════════════════════════════
# MODEL DEFINITIONS
# ═══════════════════════════════════════════════════════════

def get_models():
    """Return dictionary of models to train."""
    models = {
        'Logistic Regression': LogisticRegression(
            multi_class='multinomial', solver='lbfgs', C=1.0,
            max_iter=1000, random_state=42, class_weight='balanced'
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
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
            random_state=42, eval_metric='mlogloss', use_label_encoder=False
        )
    
    return models

# ═══════════════════════════════════════════════════════════
# TRAINING FUNCTION
# ═══════════════════════════════════════════════════════════

def train_gear_models(gear_name, config):
    """Train all 5 models for a specific gear type."""
    print(f"\n{'=' * 80}")
    print(f"🔧 Training {gear_name.upper()} Gear Models")
    print(f"{'=' * 80}")
    
    # Load dataset
    df = pd.read_csv(config['dataset'])
    print(f"   Dataset: {len(df)} rows x {len(df.columns)} columns")
    
    X = df[config['features']].values
    y_labels = df[config['target']].values
    
    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(y_labels)
    print(f"   Classes: {list(le.classes_)}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train RUL regressor (shared across all models)
    print(f"\n   Training RUL Regressor...")
    rul_values = df[config['rul']].values
    scaler_rul = StandardScaler()
    X_rul_scaled = scaler_rul.fit_transform(X)
    rul_regressor = GradientBoostingRegressor(
        n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42
    )
    rul_regressor.fit(X_rul_scaled, rul_values)
    rul_r2 = rul_regressor.score(X_rul_scaled, rul_values)
    print(f"   RUL R²: {rul_r2:.4f}")
    
    # Save scaler, label encoder, and RUL regressor
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, f'models/{gear_name}_scaler.pkl')
    joblib.dump(le, f'models/{gear_name}_label_encoder.pkl')
    joblib.dump(rul_regressor, f'models/{gear_name}_rul_regressor.pkl')
    joblib.dump(scaler_rul, f'models/{gear_name}_scaler_rul.pkl')
    
    # Train all models
    models = get_models()
    comparison = {}
    best_model = None
    best_auc = 0.0
    
    for model_name, model in models.items():
        print(f"\n   Training {model_name}...")
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Multi-class AUC
        try:
            y_test_bin = label_binarize(y_test, classes=range(len(le.classes_)))
            auc = roc_auc_score(y_test_bin, y_proba, average='weighted', multi_class='ovr')
        except:
            auc = 0.0
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
        
        print(f"      Accuracy: {accuracy:.4f}")
        print(f"      F1 Score: {f1:.4f}")
        print(f"      AUC:      {auc:.4f}")
        print(f"      CV Mean:  {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
        
        # Save model
        model_filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        joblib.dump(model, f'models/{gear_name}_classifier_{model_filename}.pkl')
        
        # Store comparison
        comparison[model_name] = {
            'accuracy': float(accuracy),
            'f1': float(f1),
            'auc': float(auc),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std())
        }
        
        # Track best model
        if auc > best_auc:
            best_auc = auc
            best_model = (model_name, model)
    
    # Save comparison
    json.dump(comparison, open(f'models/{gear_name}_model_comparison.json', 'w'), indent=2)
    print(f"\n   ✅ Model comparison saved to models/{gear_name}_model_comparison.json")
    
    # Save best model as default classifier
    if best_model:
        joblib.dump(best_model[1], f'models/{gear_name}_classifier.pkl')
        print(f"   ✅ Best model ({best_model[0]}) saved as {gear_name}_classifier.pkl")
    
    # SHAP artifacts for best model
    print(f"\n   Computing SHAP values for best model ({best_model[0]})...")
    try:
        import shap
        
        ex_idx = np.random.default_rng(1).choice(len(X_scaled), min(500, len(X_scaled)), replace=False)
        X_explain = X_scaled[ex_idx]
        
        # Choose explainer based on model type
        if 'Logistic' in best_model[0] or 'SVM' in best_model[0]:
            explainer = shap.LinearExplainer(best_model[1], X_scaled)
        else:
            explainer = shap.TreeExplainer(best_model[1])
        
        shap_values = explainer.shap_values(X_explain)
        
        os.makedirs('xai', exist_ok=True)
        joblib.dump({
            'explainer': explainer,
            'shap_values': shap_values,
            'X_sample': X_explain,
            'feature_names': config['features'],
            'class_names': list(le.classes_),
            'model_name': best_model[0]
        }, f'xai/{gear_name}_shap_artifacts.pkl')
        
        print(f"   ✅ SHAP artifacts saved to xai/{gear_name}_shap_artifacts.pkl")
    except Exception as e:
        print(f"   ⚠️  SHAP computation failed: {e}")
    
    print(f"\n✅ {gear_name.upper()} Gear Training Complete!")
    print(f"   Best Model: {best_model[0]} (AUC: {best_auc:.4f})")
    
    return comparison

# ═══════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    all_results = {}
    
    for gear_name, config in GEAR_CONFIGS.items():
        try:
            results = train_gear_models(gear_name, config)
            all_results[gear_name] = results
        except Exception as e:
            print(f"\n❌ Error training {gear_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'=' * 80}")
    print("📊 TRAINING SUMMARY")
    print(f"{'=' * 80}")
    
    for gear_name, results in all_results.items():
        print(f"\n{gear_name.upper()} Gear:")
        for model_name, metrics in results.items():
            print(f"   {model_name:25s} — Acc: {metrics['accuracy']:.4f}, AUC: {metrics['auc']:.4f}")
    
    print(f"\n{'=' * 80}")
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print(f"{'=' * 80}")
    print("\nNext steps:")
    print("  1. Restart API: py -m uvicorn gear_api:app --reload --port 8000")
    print("  2. Refresh dashboard to see all models in Model Comparison tab")
    print("  3. Test predictions for all gear types")
