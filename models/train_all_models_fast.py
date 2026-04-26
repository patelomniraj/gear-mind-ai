"""
FAST ENHANCED MODEL TRAINING — All Gear Types with 5 Models Each
Optimized for speed with reduced estimators and parallel processing
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
print("🚀 FAST ENHANCED MODEL TRAINING")
print("=" * 80)

# Check actual column names
def check_columns(dataset_path):
    df = pd.read_csv(dataset_path)
    print(f"   Columns: {df.columns.tolist()}")
    return df.columns.tolist()

# Spur dataset check
print("\nChecking Spur dataset...")
spur_cols = check_columns('data/spur_gear_svm_dataset.csv')

# Bevel dataset check  
print("\nChecking Bevel dataset...")
bevel_cols = check_columns('data/bevel_rul_dataset.csv')

# Configuration with correct column names
GEAR_CONFIGS = {
    'spur': {
        'dataset': 'data/spur_gear_svm_dataset.csv',
        'features': ['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 'Temperature_C', 'Shock_Load_g', 'Noise_dB'],
        'target': 'Failure',  # Correct column name
        'rul': None  # No RUL in spur dataset, will generate synthetic
    },
    'bevel': {
        'dataset': 'data/bevel_rul_dataset.csv',
        'features': ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)', 
                    'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use'],
        'target': 'RUL (cycles)',  # Will convert to failure labels
        'rul': 'RUL (cycles)',
        'is_rul_dataset': True
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

def get_models_fast():
    """Return dictionary of models with reduced complexity for speed."""
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
            kernel='rbf', C=10.0, gamma='scale',
            probability=True, random_state=42
        )
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = xgb.XGBClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42, eval_metric='mlogloss', use_label_encoder=False,
            n_jobs=-1
        )
    
    return models

def train_gear_models(gear_name, config):
    """Train all 5 models for a specific gear type."""
    print(f"\n{'=' * 80}")
    print(f"🔧 Training {gear_name.upper()} Gear Models")
    print(f"{'=' * 80}")
    
    df = pd.read_csv(config['dataset'])
    print(f"   Dataset: {len(df)} rows x {len(df.columns)} columns")
    
    X = df[config['features']].values
    
    # Handle different target formats
    if config.get('is_rul_dataset'):
        # Bevel: Convert RUL to failure labels
        rul_values = df[config['rul']].values
        y_labels = np.where(rul_values > 50000, 'No Fault',
                           np.where(rul_values > 20000, 'Minor Fault', 'Major Fault'))
    else:
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
    
    # RUL regressor
    print(f"\n   Training RUL Regressor...")
    if config['rul'] and not config.get('is_rul_dataset'):
        rul_values = df[config['rul']].values
    elif config.get('is_rul_dataset'):
        rul_values = df[config['rul']].values
    else:
        # Generate synthetic RUL for spur
        rul_values = np.where(y_labels == 'No Failure', 
                             np.random.randint(40000, 80000, len(y_labels)),
                             np.where(y_labels == 'Minor Failure',
                                     np.random.randint(10000, 40000, len(y_labels)),
                                     np.random.randint(1000, 10000, len(y_labels))))
    
    scaler_rul = StandardScaler()
    X_rul_scaled = scaler_rul.fit_transform(X)
    rul_regressor = GradientBoostingRegressor(
        n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
    )
    rul_regressor.fit(X_rul_scaled, rul_values)
    rul_r2 = rul_regressor.score(X_rul_scaled, rul_values)
    print(f"   RUL R²: {rul_r2:.4f}")
    
    # Save preprocessing
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, f'models/{gear_name}_scaler.pkl')
    joblib.dump(le, f'models/{gear_name}_label_encoder.pkl')
    joblib.dump(rul_regressor, f'models/{gear_name}_rul_regressor.pkl')
    joblib.dump(scaler_rul, f'models/{gear_name}_scaler_rul.pkl')
    
    # Train all models
    models = get_models_fast()
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
        
        try:
            y_test_bin = label_binarize(y_test, classes=range(len(le.classes_)))
            auc = roc_auc_score(y_test_bin, y_proba, average='weighted', multi_class='ovr')
        except:
            auc = 0.0
        
        # Faster CV with 3 folds
        cv_scores = cross_val_score(model, X_scaled, y, cv=3, scoring='accuracy')
        
        print(f"      Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}, CV: {cv_scores.mean():.4f}")
        
        # Save model
        model_filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        joblib.dump(model, f'models/{gear_name}_classifier_{model_filename}.pkl')
        
        comparison[model_name] = {
            'accuracy': float(accuracy),
            'f1': float(f1),
            'auc': float(auc),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std())
        }
        
        if auc > best_auc:
            best_auc = auc
            best_model = (model_name, model)
    
    # Save comparison
    json.dump(comparison, open(f'models/{gear_name}_model_comparison.json', 'w'), indent=2)
    
    # Save best model as default
    if best_model:
        joblib.dump(best_model[1], f'models/{gear_name}_classifier.pkl')
        print(f"\n   ✅ Best: {best_model[0]} (AUC: {best_auc:.4f})")
    
    return comparison

# Main execution
if __name__ == '__main__':
    all_results = {}
    
    for gear_name in ['spur', 'bevel', 'worm']:
        try:
            config = GEAR_CONFIGS[gear_name]
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
        print(f"\n{gear_name.upper()}:")
        for model_name, metrics in sorted(results.items(), key=lambda x: x[1]['auc'], reverse=True):
            print(f"   {model_name:25s} — Acc: {metrics['accuracy']:.4f}, AUC: {metrics['auc']:.4f}")
    
    print(f"\n{'=' * 80}")
    print("✅ TRAINING COMPLETE!")
    print(f"{'=' * 80}")
