"""
Check SHAP Artifacts for All Gear Types
========================================
This script verifies that SHAP artifacts are properly loaded
and can compute SHAP values for sample inputs.
"""

import joblib
import numpy as np
import os

print("🔍 Checking SHAP Artifacts...\n")

# ═══════════════════════════════════════════════════════════
# Check Helical SHAP
# ═══════════════════════════════════════════════════════════
print("1️⃣ Helical Gear SHAP")
print("─" * 50)

if os.path.exists('xai/shap_artifacts.pkl'):
    try:
        helical_shap = joblib.load('xai/shap_artifacts.pkl')
        print("✅ File loaded successfully")
        print(f"   Keys: {list(helical_shap.keys())}")
        
        if 'explainer' in helical_shap:
            print("✅ Explainer found")
            
            # Test SHAP computation
            if 'X_sample' in helical_shap:
                test_input = helical_shap['X_sample'][0:1]
                try:
                    sv = helical_shap['explainer'].shap_values(test_input)
                    print(f"✅ SHAP computation works (shape: {np.array(sv).shape})")
                except Exception as e:
                    print(f"❌ SHAP computation failed: {e}")
            else:
                print("⚠️  No X_sample found for testing")
        else:
            print("❌ No explainer found in artifacts")
    except Exception as e:
        print(f"❌ Failed to load: {e}")
else:
    print("❌ File not found: xai/shap_artifacts.pkl")

print()

# ═══════════════════════════════════════════════════════════
# Check Spur SHAP
# ═══════════════════════════════════════════════════════════
print("2️⃣ Spur Gear SHAP")
print("─" * 50)

if os.path.exists('xai/spur_shap_artifacts.pkl'):
    try:
        spur_shap = joblib.load('xai/spur_shap_artifacts.pkl')
        print("✅ File loaded successfully")
        print(f"   Keys: {list(spur_shap.keys())}")
        
        if 'explainer' in spur_shap:
            print("✅ Explainer found")
            
            # Test SHAP computation
            if 'X_sample' in spur_shap:
                test_input = spur_shap['X_sample'][0:1]
                try:
                    sv = spur_shap['explainer'].shap_values(test_input, nsamples=50)
                    print(f"✅ SHAP computation works (type: {type(sv)})")
                    if isinstance(sv, list):
                        print(f"   List of {len(sv)} arrays, first shape: {sv[0].shape}")
                    else:
                        print(f"   Shape: {np.array(sv).shape}")
                except Exception as e:
                    print(f"❌ SHAP computation failed: {e}")
            else:
                print("⚠️  No X_sample found for testing")
        else:
            print("❌ No explainer found in artifacts")
    except Exception as e:
        print(f"❌ Failed to load: {e}")
else:
    print("❌ File not found: xai/spur_shap_artifacts.pkl")

print()

# ═══════════════════════════════════════════════════════════
# Check Bevel SHAP
# ═══════════════════════════════════════════════════════════
print("3️⃣ Bevel Gear SHAP")
print("─" * 50)

if os.path.exists('xai/bevel_shap_artifacts.pkl'):
    try:
        bevel_shap = joblib.load('xai/bevel_shap_artifacts.pkl')
        print("✅ File loaded successfully")
        print(f"   Keys: {list(bevel_shap.keys())}")
        
        if 'explainer' in bevel_shap:
            print("✅ Explainer found")
            
            # Test SHAP computation
            if 'X_sample' in bevel_shap:
                test_input = bevel_shap['X_sample'][0:1]
                try:
                    sv = bevel_shap['explainer'].shap_values(test_input)
                    print(f"✅ SHAP computation works (shape: {np.array(sv).shape})")
                except Exception as e:
                    print(f"❌ SHAP computation failed: {e}")
            else:
                print("⚠️  No X_sample found for testing")
        else:
            print("❌ No explainer found in artifacts")
    except Exception as e:
        print(f"❌ Failed to load: {e}")
else:
    print("❌ File not found: xai/bevel_shap_artifacts.pkl")

print()

# ═══════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════
print("=" * 50)
print("📊 Summary")
print("=" * 50)

helical_ok = os.path.exists('xai/shap_artifacts.pkl')
spur_ok = os.path.exists('xai/spur_shap_artifacts.pkl')
bevel_ok = os.path.exists('xai/bevel_shap_artifacts.pkl')

print(f"Helical SHAP: {'✅ Available' if helical_ok else '❌ Missing'}")
print(f"Spur SHAP:    {'✅ Available' if spur_ok else '❌ Missing'}")
print(f"Bevel SHAP:   {'✅ Available' if bevel_ok else '❌ Missing'}")

if not spur_ok:
    print("\n⚠️  Spur SHAP artifacts missing!")
    print("   Run: python train_spur_svm.py")
    print("   Then check if xai/spur_shap_artifacts.pkl was created")

if not bevel_ok:
    print("\n⚠️  Bevel SHAP artifacts missing!")
    print("   Run: python train_bevel_model.py")
    print("   Then check if xai/bevel_shap_artifacts.pkl was created")

print("\n✅ Check complete!")
