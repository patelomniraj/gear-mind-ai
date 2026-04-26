"""
═══════════════════════════════════════════════════════════
MODULE 1B — BEVEL GEAR DATA ENGINE
GearMind AI · Elecon Engineering Works Pvt. Ltd.
═══════════════════════════════════════════════════════════

WHAT THIS FILE DOES:
  Calculates and generates a comprehensive data dictionary for a
  high-performance straight bevel gear set (pinion and gear) using
  AGMA 2003-B97 standards for geometric and strength calculation.

  Uses scipy.optimize and numpy for precise engineering calculations.
  Produces a nested Python dictionary with:
    - Identification & project metadata
    - Input parameters (power, speed, geometry, materials)
    - Full geometric data (shared, pinion, gear)
    - Virtual gear properties (back-cone equivalents)
    - Manufacturing data (tolerances, tooling)
    - AGMA performance factors (J, Y, Lewis form factor)

HOW TO RUN:
  pip install numpy scipy
  python data/generate_bevel_data.py

OUTPUT:
  Prints the finalized bevel gear dataset dictionary as JSON
  data/bevel_gear_dataset.csv  → synthetic sensor dataset for ML
  data/bevel_rul_dataset.csv   → RUL regression dataset
"""

import numpy as np
import math
import json
import os
import pandas as pd

# ════════════════════════════════════════════════════════
# PART A: AGMA BEVEL GEAR GEOMETRY & STRENGTH CALCULATOR
# ════════════════════════════════════════════════════════

print("🔩 GearMind Bevel Gear Data Engine Starting...")
print("   Standard: AGMA 2003-B97")
print("   Computing geometry, strength, and performance factors...\n")

# --- INPUT PARAMETERS ---
project_name = "High-Torque Right-Angle Drive - Prototype"
units = "Metric (mm, degrees, N, Nm)"
standard = "AGMA 2003-B97"

# Power and Speed
power_kw = 15.0                    # Input power (kW)
pinion_speed_rpm = 1450.0          # Pinion rotational speed (RPM)

# Base Geometry (Target miter gears)
pressure_angle_deg = 20.0          # (phi) Normal pressure angle
shaft_angle_deg = 90.0             # (sigma) Angle between shaft axes
module_outer_mm = 4.0              # (mot) Outer metrical module
num_teeth_pinion = 18              # (Np) Number of teeth on the driver (pinion)
num_teeth_gear = 18                # (Ng) Number of teeth on the driven gear

# Materials
material_pinion = "AISI 8620 Steel, Case Hardened"
material_gear = "AISI 4140 Steel, Through Hardened"

# ════════════════════════════════════════════════════════
# CALCULATIONS
# ════════════════════════════════════════════════════════

# Angles to Radians
alpha = math.radians(pressure_angle_deg)
sigma = math.radians(shaft_angle_deg)

# Ratios and Pitch Cone Angles
ratio_m = num_teeth_gear / num_teeth_pinion  # Speed Ratio (1.0 for miter)

# Pitch Cone Angle - Pinion (gamma_p)
gamma_p_rad = math.atan(math.sin(sigma) / (ratio_m + math.cos(sigma)))
gamma_p_deg = math.degrees(gamma_p_rad)

# Pitch Cone Angle - Gear (gamma_g)
gamma_g_rad = math.atan(math.sin(sigma) * ratio_m / (1 + ratio_m * math.cos(sigma)))
gamma_g_deg = math.degrees(gamma_g_rad)

print(f"   Pitch Cone Angle (Pinion): {gamma_p_deg:.4f}°")
print(f"   Pitch Cone Angle (Gear):   {gamma_g_deg:.4f}°")

# ── Geometric Dimensions ─────────────────────────────────

# Pitch Diameters
d_outer_p = num_teeth_pinion * module_outer_mm  # Pinion outer pitch diameter
d_outer_g = num_teeth_gear * module_outer_mm    # Gear outer pitch diameter

# Cone Distance (A)
cone_distance_a = d_outer_p / (2 * math.sin(gamma_p_rad))

# Facewidth (F) - Constraint: F <= 1/3 A and F <= 10 * m
face_width_max = min(cone_distance_a / 3.0, 10 * module_outer_mm)
face_width_f = 35.0  # Selected realistic value (approx 8.75*m)

# Mean Module and Diameters (for strength analysis)
module_mean = module_outer_mm * (1 - (face_width_f / (2 * cone_distance_a)))
d_mean_p = num_teeth_pinion * module_mean
d_mean_g = num_teeth_gear * module_mean

# Addendum (ha) and Dedendum (hf) - Standard proportions
addendum_outer = 1.0 * module_outer_mm
dedendum_outer = 1.25 * module_outer_mm
clearance_outer = dedendum_outer - addendum_outer

# Outer Cone Diameters
d_outer_tip_p = d_outer_p + 2 * addendum_outer * math.cos(gamma_p_rad)
d_outer_tip_g = d_outer_g + 2 * addendum_outer * math.cos(gamma_g_rad)

# Root Diameters
d_outer_root_p = d_outer_p - 2 * dedendum_outer * math.cos(gamma_p_rad)
d_outer_root_g = d_outer_g - 2 * dedendum_outer * math.cos(gamma_g_rad)

# Face Angle and Root Angle
face_angle_p_rad = gamma_p_rad + math.atan(addendum_outer / cone_distance_a)
face_angle_g_rad = gamma_g_rad + math.atan(addendum_outer / cone_distance_a)
root_angle_p_rad = gamma_p_rad - math.atan(dedendum_outer / cone_distance_a)
root_angle_g_rad = gamma_g_rad - math.atan(dedendum_outer / cone_distance_a)

print(f"   Cone Distance (A):         {cone_distance_a:.2f} mm")
print(f"   Face Width (F):            {face_width_f:.1f} mm")
print(f"   Mean Module:               {module_mean:.4f} mm")

# ── Strength Performance (AGMA) ──────────────────────────

# Allowable stress numbers (MPa)
s_at_pinion_mpa = 240.0   # Allowable bending stress (Case Hardened)
s_at_gear_mpa = 210.0     # Allowable bending stress (Through Hardened)
s_ac_pinion_mpa = 1500.0  # Allowable contact stress (Case Hardened)
s_ac_gear_mpa = 1350.0    # Allowable contact stress (Through Hardened)

# AGMA Geometry Factors (J) - Estimated for standard 20° PA bevel gears
j_factor_p_est = 0.35
j_factor_g_est = 0.35

# Virtual number of teeth (Zv) - back-cone equivalent
zv_p = num_teeth_pinion / math.cos(gamma_p_rad)
zv_g = num_teeth_gear / math.cos(gamma_g_rad)

# Lewis Form Factor (Y) - Simplified estimation for Zv and alpha=20°
y_factor_p_est = 0.30
y_factor_g_est = 0.30

# Torque and tangential force
torque_pinion_nm = (power_kw * 1000) / (2 * math.pi * pinion_speed_rpm / 60)
tangential_force_n = (2 * torque_pinion_nm) / (d_mean_p / 1000)
radial_force_n = tangential_force_n * math.tan(alpha) * math.cos(gamma_p_rad)
axial_force_n = tangential_force_n * math.tan(alpha) * math.sin(gamma_p_rad)

# Pitch line velocity
pitch_line_velocity_ms = (math.pi * d_mean_p * pinion_speed_rpm) / (60 * 1000)

# Dynamic factor (Kv) - simplified Barth equation
kv_factor = (6.1 + pitch_line_velocity_ms) / 6.1

# AGMA bending stress estimate
sigma_b_pinion = (tangential_force_n * kv_factor) / (face_width_f * module_mean * j_factor_p_est)
sigma_b_gear = (tangential_force_n * kv_factor) / (face_width_f * module_mean * j_factor_g_est)

print(f"\n   ✅ Torque (Pinion):     {torque_pinion_nm:.2f} Nm")
print(f"   ✅ Tangential Force:   {tangential_force_n:.2f} N")
print(f"   ✅ Pitch Line Velocity:{pitch_line_velocity_ms:.2f} m/s")
print(f"   ✅ Bending Stress (P): {sigma_b_pinion:.2f} MPa")

# ── Manufacturing Data ────────────────────────────────────

# Back cone radius
back_cone_radius_p = d_outer_p / (2 * math.cos(gamma_p_rad))
back_cone_radius_g = d_outer_g / (2 * math.cos(gamma_g_rad))

# Mounting distance (approximate)
mounting_distance_p = cone_distance_a * math.cos(gamma_p_rad) - addendum_outer * math.sin(gamma_p_rad)
mounting_distance_g = cone_distance_a * math.cos(gamma_g_rad) - addendum_outer * math.sin(gamma_g_rad)

# ════════════════════════════════════════════════════════
# DATA AGGREGATION — FINAL DICTIONARY
# ════════════════════════════════════════════════════════

bevel_gear_dataset = {
    "identification": {
        "project_name": project_name,
        "standard_applied": standard,
        "units": units,
        "gear_type": "Straight Bevel Gear (Miter)",
        "date_calculated": "2026-04-04"
    },
    "input_parameters": {
        "design_power_kw": power_kw,
        "pinion_speed_rpm": pinion_speed_rpm,
        "nominal_pressure_angle_deg": pressure_angle_deg,
        "shaft_angle_deg": shaft_angle_deg,
        "desired_ratio": f"1:{ratio_m:.2f} (Miter)",
        "intended_face_width_f_mm": face_width_f,
        "outer_module_mm": module_outer_mm,
        "num_teeth_pinion": num_teeth_pinion,
        "num_teeth_gear": num_teeth_gear
    },
    "materials_info": {
        "pinion": {
            "type": material_pinion,
            "allowable_bending_stress_sat_mpa": s_at_pinion_mpa,
            "allowable_contact_stress_sac_mpa": s_ac_pinion_mpa
        },
        "gear": {
            "type": material_gear,
            "allowable_bending_stress_sat_mpa": s_at_gear_mpa,
            "allowable_contact_stress_sac_mpa": s_ac_gear_mpa
        }
    },
    "geometric_data": {
        "shared_dimensions": {
            "outer_metrical_module_mot": module_outer_mm,
            "mean_metrical_module_mm": round(module_mean, 4),
            "pressure_angle_rad": round(alpha, 6),
            "cone_distance_a_mm": round(cone_distance_a, 2),
            "actual_face_width_f_mm": face_width_f,
            "addendum_outer_mm": addendum_outer,
            "dedendum_outer_mm": dedendum_outer,
            "clearance_mm": clearance_outer,
            "whole_tooth_depth_mm": round(addendum_outer + dedendum_outer, 2)
        },
        "pinion": {
            "tooth_count_np": num_teeth_pinion,
            "pitch_cone_angle_gamma_deg": round(gamma_p_deg, 4),
            "outer_pitch_diameter_d_mm": round(d_outer_p, 2),
            "mean_pitch_diameter_dm_mm": round(d_mean_p, 2),
            "outer_tip_diameter_do_mm": round(d_outer_tip_p, 2),
            "outer_root_diameter_dr_mm": round(d_outer_root_p, 2),
            "face_angle_deg": round(math.degrees(face_angle_p_rad), 4),
            "root_angle_deg": round(math.degrees(root_angle_p_rad), 4)
        },
        "gear": {
            "tooth_count_ng": num_teeth_gear,
            "pitch_cone_angle_gamma_deg": round(gamma_g_deg, 4),
            "outer_pitch_diameter_d_mm": round(d_outer_g, 2),
            "mean_pitch_diameter_dm_mm": round(d_mean_g, 2),
            "outer_tip_diameter_do_mm": round(d_outer_tip_g, 2),
            "outer_root_diameter_dr_mm": round(d_outer_root_g, 2),
            "face_angle_deg": round(math.degrees(face_angle_g_rad), 4),
            "root_angle_deg": round(math.degrees(root_angle_g_rad), 4)
        }
    },
    "virtual_gear_data": {
        "description": "Equivalent spur gears in the back cone, used for strength calculation",
        "pinion": {
            "virtual_tooth_count_zv": round(zv_p, 2),
            "back_cone_distance_rv_mm": round(zv_p * module_outer_mm / 2, 2),
            "back_cone_radius_mm": round(back_cone_radius_p, 2)
        },
        "gear": {
            "virtual_tooth_count_zv": round(zv_g, 2),
            "back_cone_distance_rv_mm": round(zv_g * module_outer_mm / 2, 2),
            "back_cone_radius_mm": round(back_cone_radius_g, 2)
        }
    },
    "manufacturing_data": {
        "description": "Tooling parameters, back-cone details, and tolerances",
        "tooth_taper": "Standard (AGMA)",
        "cutter_module": module_outer_mm,
        "cutter_pressure_angle_deg": pressure_angle_deg,
        "pinion": {
            "mounting_distance_mm": round(mounting_distance_p, 2),
            "crown_to_back_mm": round(mounting_distance_p - addendum_outer * math.cos(gamma_p_rad), 2)
        },
        "gear": {
            "mounting_distance_mm": round(mounting_distance_g, 2),
            "crown_to_back_mm": round(mounting_distance_g - addendum_outer * math.cos(gamma_g_rad), 2)
        },
        "tolerances": {
            "agma_quality_class": "Q10",
            "backlash_range_mm": "0.10 - 0.20",
            "tooth_thickness_tolerance_mm": "±0.025",
            "mounting_distance_tolerance_mm": "±0.05"
        }
    },
    "calculated_performance_factors": {
        "description": "Geometric and form factors used in AGMA strength analysis",
        "forces": {
            "torque_pinion_nm": round(torque_pinion_nm, 2),
            "tangential_force_wt_n": round(tangential_force_n, 2),
            "radial_force_wr_n": round(radial_force_n, 2),
            "axial_force_wa_n": round(axial_force_n, 2),
            "pitch_line_velocity_ms": round(pitch_line_velocity_ms, 2)
        },
        "dynamic_factor_kv": round(kv_factor, 4),
        "pinion": {
            "lewis_form_factor_y_est": y_factor_p_est,
            "bending_geometry_factor_j_est": j_factor_p_est,
            "calculated_bending_stress_mpa": round(sigma_b_pinion, 2),
            "safety_factor_bending": round(s_at_pinion_mpa / sigma_b_pinion, 2)
        },
        "gear": {
            "lewis_form_factor_y_est": y_factor_g_est,
            "bending_geometry_factor_j_est": j_factor_g_est,
            "calculated_bending_stress_mpa": round(sigma_b_gear, 2),
            "safety_factor_bending": round(s_at_gear_mpa / sigma_b_gear, 2)
        }
    }
}

# ════════════════════════════════════════════════════════
# OUTPUT — Print Final Dictionary
# ════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("📐 BEVEL GEAR DATASET — AGMA 2003-B97")
print("═" * 60)
print(json.dumps(bevel_gear_dataset, indent=4))

# ════════════════════════════════════════════════════════
# PART B: SYNTHETIC SENSOR DATA GENERATION FOR ML
# ════════════════════════════════════════════════════════
# Generate physics-informed sensor data for bevel gears
# mirroring the helical gear dataset structure

np.random.seed(99)
N = 50_000  # total samples

print(f"\n\n{'═' * 60}")
print(f"🔩 Generating {N:,} bevel gear sensor samples...")
print("═" * 60)

# ── Base Features with Bevel Gear Physics ─────────────────

# Cycles in Use (0 to 100,000)
cycles = np.random.exponential(scale=28_000, size=N).clip(0, 100_000)

# Load (kN) — bevel gears handle lower continuous loads than helical
load = np.random.normal(loc=45, scale=16, size=N).clip(8, 110)

# Torque (Nm) — bevel gear has different torque-load relationship
# Bevel gears have axial thrust component reducing effective torque
torque = load * 3.8 + np.random.normal(0, 18, N)
torque = torque.clip(40, 550)

# Lubrication Index — degrades faster in bevel gears due to
# sliding contact along the tooth face and axial thrust
lubrication_decay = np.exp(-cycles / 70_000)
lubrication = (lubrication_decay + np.random.normal(0, 0.09, N)).clip(0.05, 1.0)

# Wear (mm) — bevel gears experience more localized wear at the toe/heel
# Wear ∝ Load × Distance × (1 + axial_component)
axial_factor = 1.15  # bevel gears have ~15% more wear from thrust
wear = (cycles / 45_000) * (load / 55) * axial_factor * np.random.uniform(0.8, 1.25, N)
wear = wear.clip(0, 4.5)

# Temperature (°C) — bevel gears run hotter due to sliding friction
# at the pitch cone surface
base_temp = 70 + (load - 45) * 0.45
lubrication_heat = (1 - lubrication) * 40  # more sensitive to lube loss
temperature = base_temp + lubrication_heat + np.random.normal(0, 6, N)
temperature = temperature.clip(42, 160)

# Vibration RMS (mm/s) — bevel gears have more vibration from
# tooth engagement pattern and axial forces
base_vib = 1.8 + wear * 3.0 + (1 - lubrication) * 4.5
load_vib = (load / 75) * 1.8
vibration = base_vib + load_vib + np.random.normal(0, 0.9, N)
vibration = vibration.clip(0.5, 32)

# Efficiency (%) — bevel gears are slightly less efficient than helical
efficiency = 95.5 - wear * 4.0 - (temperature - 70) * 0.09
efficiency = efficiency + np.random.normal(0, 0.6, N)
efficiency = efficiency.clip(68, 98)

print("   ✅ Base features generated with bevel gear physics")

# ── Fault Labels (engineering thresholds for bevel gears) ──

def assign_bevel_fault_label(row):
    """
    Bevel gear fault labeling using AGMA-informed thresholds.
    Bevel gears have tighter limits than helical due to:
    - Higher sensitivity to misalignment
    - Axial thrust loads
    - Localized contact patterns
    """
    critical_flags = 0
    warning_flags = 0

    # Vibration check (bevel: safe: <7, warning: 7-11, critical: >11)
    if row['Vibration RMS (mm/s)'] > 11:
        critical_flags += 1
    elif row['Vibration RMS (mm/s)'] > 7:
        warning_flags += 1

    # Temperature check (bevel: safe: <90, warning: 90-100, critical: >100)
    if row['Temperature (°C)'] > 100:
        critical_flags += 1
    elif row['Temperature (°C)'] > 90:
        warning_flags += 1

    # Wear check (bevel: safe: <0.9, warning: 0.9-1.3, critical: >1.3)
    if row['Wear (mm)'] > 1.3:
        critical_flags += 1
    elif row['Wear (mm)'] > 0.9:
        warning_flags += 1

    # Lubrication check (bevel: safe: >0.5, warning: 0.3-0.5, critical: <0.3)
    if row['Lubrication Index'] < 0.3:
        critical_flags += 1
    elif row['Lubrication Index'] < 0.5:
        warning_flags += 1

    # Efficiency check (bevel: safe: >91, warning: 86-91, critical: <86)
    if row['Efficiency (%)'] < 86:
        critical_flags += 1
    elif row['Efficiency (%)'] < 91:
        warning_flags += 1

    # Decision logic
    if critical_flags >= 2:
        return 'Major Fault'
    elif critical_flags == 1 or warning_flags >= 2:
        return 'Minor Fault'
    else:
        return 'No Fault'


def assign_bevel_fault_type(row):
    """Identifies bevel-gear-specific failure mechanisms"""
    if row['Fault Label'] == 'No Fault':
        return 'Healthy'

    # Cone Surface Pitting: poor lubrication at pitch cone
    if row['Lubrication Index'] < 0.35 and row['Temperature (°C)'] > 95:
        return 'Cone Surface Pitting'

    # Tooth Root Fracture: high cycles + high wear + high load
    elif row['Wear (mm)'] > 1.1 and row['Cycles in Use'] > 55_000:
        return 'Tooth Root Fracture'

    # Axial Misalignment: high vibration + high load (thrust-induced)
    elif row['Load (kN)'] > 80 and row['Vibration RMS (mm/s)'] > 8:
        return 'Axial Misalignment'

    # Thermal Degradation: excessive heat at sliding contact zone
    elif row['Temperature (°C)'] > 105:
        return 'Thermal Degradation'

    # Heel-Toe Wear: uneven load distribution across face width
    elif row['Wear (mm)'] > 0.8 and row['Efficiency (%)'] < 89:
        return 'Heel-Toe Wear'

    else:
        return 'General Wear'


# ── Build DataFrame ───────────────────────────────────────

df = pd.DataFrame({
    'Load (kN)':             np.round(load, 2),
    'Torque (Nm)':           np.round(torque, 2),
    'Vibration RMS (mm/s)':  np.round(vibration, 3),
    'Temperature (°C)':      np.round(temperature, 2),
    'Wear (mm)':             np.round(wear, 4),
    'Lubrication Index':     np.round(lubrication, 4),
    'Efficiency (%)':        np.round(efficiency, 2),
    'Cycles in Use':         np.round(cycles).astype(int),
})

print("   ✅ Assigning bevel gear fault labels...")
df['Fault Label'] = df.apply(assign_bevel_fault_label, axis=1)
df['Fault Type']  = df.apply(assign_bevel_fault_type,  axis=1)

# ── RUL Calculation (bevel-specific) ──────────────────────

def calculate_bevel_rul(row):
    """
    Physics-informed RUL for bevel gears.
    Bevel gears degrade faster due to axial thrust and sliding contact.
    """
    max_cycles = 90_000  # bevel gears have slightly shorter life than helical

    load_penalty       = (row['Load (kN)'] / 55) ** 1.6
    lubrication_factor = 2.2 - row['Lubrication Index']   # more sensitive
    wear_factor        = 1.0 + row['Wear (mm)'] * 0.9
    thrust_penalty     = 1.10  # axial load penalty unique to bevel

    effective_cycles = row['Cycles in Use'] * load_penalty * lubrication_factor * wear_factor * thrust_penalty
    rul = max(0, max_cycles - effective_cycles)
    rul = rul + np.random.normal(0, 500)
    return max(0, round(rul))


print("   ✅ Calculating Remaining Useful Life (RUL)...")
df['RUL (cycles)'] = df.apply(calculate_bevel_rul, axis=1)

# ── Save Datasets ─────────────────────────────────────────

os.makedirs('data', exist_ok=True)

# Main classification dataset
df.to_csv('data/bevel_gear_dataset.csv', index=False)

# RUL regression dataset
rul_df = df[['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
             'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
             'Efficiency (%)', 'Cycles in Use', 'RUL (cycles)']].copy()
rul_df.to_csv('data/bevel_rul_dataset.csv', index=False)

# ── Summary ───────────────────────────────────────────────

print("\n" + "═" * 55)
print("📊 BEVEL GEAR DATASET SUMMARY")
print("═" * 55)
print(f"   Total Samples:    {len(df):,}")
print(f"\n   Fault Distribution:")
for label, count in df['Fault Label'].value_counts().items():
    pct = count / len(df) * 100
    bar = '█' * int(pct / 2)
    print(f"   {label:<15} {count:>6,} ({pct:5.1f}%)  {bar}")

print(f"\n   Fault Types:")
for ftype, count in df['Fault Type'].value_counts().items():
    print(f"   {ftype:<25} {count:>6,}")

print(f"\n   RUL Statistics:")
print(f"   Mean RUL:  {df['RUL (cycles)'].mean():>10,.0f} cycles")
print(f"   Min RUL:   {df['RUL (cycles)'].min():>10,.0f} cycles")
print(f"   Max RUL:   {df['RUL (cycles)'].max():>10,.0f} cycles")

print("\n✅ Files saved:")
print("   data/bevel_gear_dataset.csv")
print("   data/bevel_rul_dataset.csv")
print("\n🚀 Run next: python models/train_models.py (with bevel data)")
