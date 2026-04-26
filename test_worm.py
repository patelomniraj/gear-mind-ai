"""
Quick test script for Worm Gear API
"""
import requests
import json

print("🧪 Testing GearMind AI - Worm Gear Prediction")
print("=" * 60)

# Test 1: Check API is running
print("\n1️⃣ Testing API connection...")
try:
    response = requests.get("http://localhost:8000")
    if response.status_code == 200:
        print("   ✅ API is running!")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ API returned status code: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot connect to API: {e}")
    print("   Make sure API is running: py -m uvicorn gear_api:app --reload --port 8000")
    exit(1)

# Test 2: Worm Gear Prediction
print("\n2️⃣ Testing Worm Gear prediction...")
worm_payload = {
    "gear_type": "Worm",
    "load": 1321.0,      # Worm_RPM
    "torque": 86.8,      # Input_Torque
    "vib": 5.2,          # Axial_Vib
    "temp": 56.5,        # Oil_Temp
    "wear": 2.3,         # Radial_Vib
    "lube": 0.85,        # Efficiency_Calc (normalized)
    "eff": 85.0,         # Efficiency_Calc
    "cycles": 155139     # RUL_Cycles
}

try:
    response = requests.post(
        "http://localhost:8000/api/predict",
        json=worm_payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Prediction successful!")
        print(f"\n   📊 Results:")
        print(f"   Fault Label:    {result['fault_label']}")
        print(f"   Confidence:     {result['confidence']:.2%}")
        print(f"   Health Score:   {result.get('health_score', 'N/A')}/100")
        print(f"   RUL Cycles:     {result['rul_cycles']:,}")
        print(f"   Anomaly Status: {result['anomaly_status']}")
        
        print(f"\n   🎯 Class Probabilities:")
        for cls, prob in result['class_probs'].items():
            print(f"      {cls:15s}: {prob:.2%}")
        
        if result.get('violations'):
            print(f"\n   ⚠️  Violations detected:")
            for feat, info in result['violations'].items():
                print(f"      {feat}: {info['value']} (safe: {info['safe_min']}-{info['safe_max']}) [{info['severity']}]")
        else:
            print(f"\n   ✅ All parameters within safe range")
            
    else:
        print(f"   ❌ Prediction failed with status code: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Prediction error: {e}")
    exit(1)

# Test 3: Model Comparison
print("\n3️⃣ Testing Model Comparison endpoint...")
try:
    response = requests.get("http://localhost:8000/api/models/comparison")
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Model comparison retrieved!")
        print(f"\n   📈 Overall Statistics:")
        overall = data['overall']
        print(f"      Total Gear Types: {overall['total_gear_types']}")
        print(f"      Total Models:     {overall['total_models']}")
        print(f"      Avg Accuracy:     {overall['avg_accuracy']:.2%}")
        print(f"      Avg F1 Score:     {overall['avg_f1']:.2%}")
        print(f"      Avg AUC:          {overall['avg_auc']:.2%}")
        print(f"      Best AUC:         {overall['best_auc']:.4f}")
    else:
        print(f"   ⚠️  Model comparison returned status code: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Model comparison error: {e}")

# Test 4: Gear Configs
print("\n4️⃣ Testing Gear Configurations...")
try:
    response = requests.get("http://localhost:8000/api/gear-configs")
    if response.status_code == 200:
        configs = response.json()
        print("   ✅ Gear configurations retrieved!")
        print(f"\n   🌀 Worm Gear Config:")
        worm = configs.get('Worm', {})
        print(f"      Icon:        {worm.get('icon', 'N/A')}")
        print(f"      Spec:        {worm.get('spec', 'N/A')}")
        print(f"      Description: {worm.get('description', 'N/A')[:60]}...")
        print(f"      Units:       {len(worm.get('units', {}))} sample units")
    else:
        print(f"   ⚠️  Gear configs returned status code: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Gear configs error: {e}")

print("\n" + "=" * 60)
print("✅ All tests completed successfully!")
print("\nNext steps:")
print("  1. Open dashboard: http://localhost:5173")
print("  2. Navigate to Model Comparison tab")
print("  3. Select 'Overall Comparison' from dropdown")
print("  4. Generate a report and check testing/ folder")
print("=" * 60)
