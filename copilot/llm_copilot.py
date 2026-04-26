"""
MODULE 4 — LLM COPILOT (Groq — FREE & FAST)
GearMind AI · Elecon Engineering Works Pvt. Ltd.
"""

import os
import json
import numpy as np
import joblib
from groq import Groq

model      = joblib.load('models/best_classifier.pkl')
rul_model  = joblib.load('models/rul_regressor.pkl')
scaler     = joblib.load('models/scaler.pkl')
scaler_rul = joblib.load('models/scaler_rul.pkl')
le         = joblib.load('models/label_encoder.pkl')

try:
    shap_data     = joblib.load('xai/shap_artifacts.pkl')
    anomaly_model = joblib.load('xai/anomaly_model.pkl')
    XAI_AVAILABLE = True
except:
    XAI_AVAILABLE = False

FEATURE_COLS = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]

SAFE_RANGES = {
    'Load (kN)':            (10, 80),
    'Torque (Nm)':          (50, 400),
    'Vibration RMS (mm/s)': (0, 6),
    'Temperature (°C)':     (40, 95),
    'Wear (mm)':            (0, 1.0),
    'Lubrication Index':    (0.5, 1.0),
    'Efficiency (%)':       (93, 99),
    'Cycles in Use':        (0, 100000),
}

def predict_gear_health(sensor_values: dict) -> dict:
    input_array  = np.array([sensor_values[f] for f in FEATURE_COLS])
    input_scaled = scaler.transform(input_array.reshape(1, -1))

    pred_encoded = model.predict(input_scaled)[0]
    pred_label   = le.inverse_transform([pred_encoded])[0]
    pred_proba   = model.predict_proba(input_scaled)[0]
    confidence   = pred_proba.max()
    class_probs  = dict(zip(le.classes_, pred_proba))

    input_rul_scaled = scaler_rul.transform(input_array.reshape(1, -1))
    rul_cycles       = max(0, int(rul_model.predict(input_rul_scaled)[0]))

    shap_values = {}
    if XAI_AVAILABLE:
        try:
            explainer = shap_data['explainer']
            sv = explainer.shap_values(input_scaled)
            # sv shape: (n_samples, n_features, n_classes) for XGBoost multiclass
            # pred_encoded: 0=Major Fault, 1=Minor Fault, 2=No Fault (alphabetical)
            if hasattr(sv, 'ndim') and sv.ndim == 3:
                # Get SHAP for the PREDICTED class
                sv_for_class = sv[0, :, pred_encoded]
            elif isinstance(sv, list):
                sv_for_class = sv[min(pred_encoded, len(sv)-1)][0]
            else:
                sv_for_class = sv[0]
            
            # For No Fault class: flip sign so green = good (pushing toward no fault)
            # No Fault is typically class index 2 (alphabetical: Major=0, Minor=1, No=2)
            no_fault_idx = list(le.classes_).index("No Fault") if "No Fault" in list(le.classes_) else -1
            if pred_encoded == no_fault_idx:
                sv_for_class = -sv_for_class  # flip: positive now means "safe"
            
            shap_values = dict(zip(FEATURE_COLS, sv_for_class.tolist()))
        except:
            shap_values = {}

    anomaly_score  = 0.0
    anomaly_status = "UNKNOWN"
    if XAI_AVAILABLE:
        try:
            score  = anomaly_model.decision_function(input_scaled)[0]
            status = anomaly_model.predict(input_scaled)[0]
            anomaly_score  = float(score)
            anomaly_status = "NORMAL" if status == 1 else "SUSPICIOUS"
        except:
            pass

    violations = {}
    for feat, (low, high) in SAFE_RANGES.items():
        val = sensor_values[feat]
        if val < low or val > high:
            violations[feat] = {
                'value': val, 'safe_min': low, 'safe_max': high,
                'severity': 'CRITICAL' if (val < low * 0.8 or val > high * 1.2) else 'WARNING'
            }

    return {
        'fault_label':    pred_label,
        'confidence':     float(confidence),
        'class_probs':    class_probs,
        'rul_cycles':     rul_cycles,
        'shap_values':    shap_values,
        'anomaly_score':  anomaly_score,
        'anomaly_status': anomaly_status,
        'violations':     violations,
        'sensor_values':  sensor_values,
    }

def build_gear_context(prediction: dict, gear_id: str) -> str:
    sv   = prediction['sensor_values']
    shap = prediction['shap_values']

    shap_sorted = sorted(shap.items(), key=lambda x: abs(x[1]), reverse=True)
    shap_text   = "\n".join([
        f"  - {feat}: {val:+.3f} ({'pushes toward fault' if val > 0 else 'pushes away from fault'})"
        for feat, val in shap_sorted[:5]
    ]) if shap_sorted else "  Not available"

    viol_text = ""
    for feat, info in prediction['violations'].items():
        viol_text += f"  - {feat}: {info['value']} (safe: {info['safe_min']}–{info['safe_max']}) [{info['severity']}]\n"
    if not viol_text:
        viol_text = "  None — all parameters within safe range\n"

    shifts_remaining = prediction['rul_cycles'] // 400

    return f"""You are GearMind AI, an expert helical gear maintenance assistant for Elecon Engineering Works, Anand, Gujarat.
You have access to real-time ML model predictions and live sensor data. Be concise, specific, and actionable.

GEAR: {gear_id}
Fault: {prediction['fault_label']} ({prediction['confidence']:.1%} confidence)
Anomaly: {prediction['anomaly_status']}
RUL: ~{prediction['rul_cycles']:,} cycles (~{shifts_remaining} shifts)

Probabilities: No Fault {prediction['class_probs'].get('No Fault', 0):.1%} | Minor {prediction['class_probs'].get('Minor Fault', 0):.1%} | Major {prediction['class_probs'].get('Major Fault', 0):.1%}

SENSORS:
  Load: {sv['Load (kN)']:.1f} kN (safe: 10-80)
  Torque: {sv['Torque (Nm)']:.1f} Nm (safe: 50-400)
  Vibration: {sv['Vibration RMS (mm/s)']:.2f} mm/s (safe: <6)
  Temperature: {sv['Temperature (°C)']:.1f}°C (safe: <95)
  Wear: {sv['Wear (mm)']:.3f} mm (safe: <1.0)
  Lubrication: {sv['Lubrication Index']:.3f} (safe: >0.5)
  Efficiency: {sv['Efficiency (%)']:.1f}% (safe: >93)
  Cycles: {sv['Cycles in Use']:,.0f}

OUT OF RANGE: {viol_text}
SHAP TOP DRIVERS:
{shap_text}

Cost context: Preventive maintenance ~₹40,000-80,000 | Failure cost ~₹2-5 lakhs
Answer like a senior maintenance engineer. Use bullet points. Be direct and specific."""

def ask_gearmind(question: str, prediction: dict, gear_id: str, chat_history: list = None) -> str:
    client  = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    context = build_gear_context(prediction, gear_id)

    messages = [{"role": "system", "content": context}]
    if chat_history:
        messages.extend(chat_history[-8:])
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return response.choices[0].message.content

def generate_maintenance_report(prediction: dict, gear_id: str) -> str:
    client  = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    context = build_gear_context(prediction, gear_id)

    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": f"""Generate a comprehensive professional maintenance report for {gear_id} with these sections:

1. EXECUTIVE SUMMARY
   - Overall health status and criticality level
   - Key findings in 2-3 sentences
   - Immediate action required (Yes/No)

2. FAULT ASSESSMENT
   - Fault type: {prediction['fault_label']}
   - Confidence level: {prediction['confidence']:.1%}
   - Severity classification (Critical/Warning/Normal)
   - Anomaly detection status: {prediction['anomaly_status']}

3. SENSOR ANALYSIS
   - Current readings for all sensors with actual numeric values
   - Out-of-range parameters with safe limits
   - Trend analysis (increasing/stable/decreasing)

4. ROOT CAUSE ANALYSIS
   - Primary contributing factors (reference SHAP values)
   - Secondary factors
   - Correlation between parameters

5. REMAINING USEFUL LIFE (RUL)
   - Estimated cycles: {prediction['rul_cycles']:,}
   - Estimated shifts: {prediction['rul_cycles'] // 400}
   - Estimated days at current usage
   - Confidence interval

6. RECOMMENDED ACTIONS
   - Immediate actions (0-4 hours)
   - Short-term actions (24-48 hours)
   - Medium-term actions (1 week)
   - Long-term preventive measures
   - Each action should be numbered and specific

7. COST-BENEFIT ANALYSIS
   - Preventive maintenance cost estimate (INR)
   - Failure cost estimate (INR)
   - Potential savings (INR)
   - ROI calculation
   - Downtime cost analysis

8. POST-MAINTENANCE MONITORING PROTOCOL
   - Parameters to monitor closely
   - Monitoring frequency
   - Success criteria
   - Follow-up inspection schedule

9. TECHNICAL SPECIFICATIONS
   - Gear ID: {gear_id}
   - Report generation timestamp
   - Model confidence metrics
   - Data quality indicators

Be specific with all sensor values, use actual numbers from the data, avoid placeholder text like [value] or [number]. Format numbers properly with commas for thousands."""}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=3000,
        temperature=0.5,
    )
    return response.choices[0].message.content

def simulate_what_if(original_sensors: dict, modified_feature: str, new_value: float, gear_id: str) -> dict:
    original_pred    = predict_gear_health(original_sensors)
    modified_sensors = original_sensors.copy()
    modified_sensors[modified_feature] = new_value
    modified_pred    = predict_gear_health(modified_sensors)
    delta_rul        = modified_pred['rul_cycles'] - original_pred['rul_cycles']

    explanation = ""
    if os.environ.get("GROQ_API_KEY"):
        client  = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        context = build_gear_context(original_pred, gear_id)
        prompt  = f"""What happens if {modified_feature} changes from {original_sensors[modified_feature]} to {new_value}?
Before: {original_pred['fault_label']} ({original_pred['confidence']:.1%}), RUL: {original_pred['rul_cycles']:,} cycles
After:  {modified_pred['fault_label']} ({modified_pred['confidence']:.1%}), RUL: {modified_pred['rul_cycles']:,} cycles (change: {delta_rul:+,})
Explain in 4-5 sentences: impact on fault status, RUL change, feasibility, and whether other actions are needed."""

        response    = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": context}, {"role": "user", "content": prompt}],
            max_tokens=400,
        )
        explanation = response.choices[0].message.content

    return {'explanation': explanation, 'original_pred': original_pred, 'modified_pred': modified_pred, 'rul_delta': delta_rul}
