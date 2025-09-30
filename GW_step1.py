# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 12:46:06 2025

@author: sercan.yalcin
"""

# GW_step1.py
# Run: streamlit run GW_step1.py

import streamlit as st
import math

st.set_page_config(page_title="PV Stringing Checker — Step 1", page_icon="🔌", layout="centered")

st.title("🔌 PV Stringing Checker — Step 1")

# -----------------------------
# Inverter database (hard-coded)
# -----------------------------
INVERTERS = {
    # HT Series
    "GW225K-HT": {
        "series": "HT",
        "Vdc_max": 1500,
        "MPPT_vmin": 500, "MPPT_vmax": 1500,
        "Isc_mppt_max": 50,  # A
        "Imp_mppt_max": 30,  # A
        "mppt_count": 12,
        "strings_per_mppt": 2,
        "S_ac_kVA": 225,
        "efficiency_pct": 98.5,
        "derated_rule": "none",  # OLTC worst-case derating: none for 225
    },
    "GW250K-HT": {
        "series": "HT",
        "Vdc_max": 1500,
        "MPPT_vmin": 500, "MPPT_vmax": 1500,
        "Isc_mppt_max": 50,
        "Imp_mppt_max": 30,
        "mppt_count": 12,
        "strings_per_mppt": 2,
        "S_ac_kVA": 250,
        "efficiency_pct": 98.5,
        "derated_rule": "minus10pct",  # Step 3'te AC derating uygulanacak
    },
    "GW225KN-HT": {
        "series": "HT",
        "Vdc_max": 1500,
        "MPPT_vmin": 500, "MPPT_vmax": 1500,
        "Isc_mppt_max": 90,
        "Imp_mppt_max": 60,
        "mppt_count": 6,
        "strings_per_mppt": 3,
        "S_ac_kVA": 225,
        "efficiency_pct": 98.5,
        "derated_rule": "none",
    },
    "GW250KN-HT": {
        "series": "HT",
        "Vdc_max": 1500,
        "MPPT_vmin": 500, "MPPT_vmax": 1500,
        "Isc_mppt_max": 90,
        "Imp_mppt_max": 60,
        "mppt_count": 6,
        "strings_per_mppt": 3,
        "S_ac_kVA": 250,
        "efficiency_pct": 98.5,
        "derated_rule": "minus10pct",
    },
    # UT Series
    "GW320K-UT": {
        "series": "UT",
        "Vdc_max": 1500,
        "MPPT_vmin": 480, "MPPT_vmax": 1500,
        "Isc_mppt_max": 50,
        "Imp_mppt_max": 30,
        "mppt_count": 15,
        "strings_per_mppt": 2,
        "S_ac_kVA": 320,
        "efficiency_pct": 98.8,
        "derated_rule": "to315",  # OLTC worst-case: 315 kVA'a sabitlenecek
    },
    "GW320KH-UT": {
        "series": "UT",
        "Vdc_max": 1500,
        "MPPT_vmin": 480, "MPPT_vmax": 1500,
        "Isc_mppt_max": 60,
        "Imp_mppt_max": 40,
        "mppt_count": 12,
        "strings_per_mppt": 2,
        "S_ac_kVA": 320,
        "efficiency_pct": 98.8,
        "derated_rule": "to315",
    },
    "GW350K-UT": {
        "series": "UT",
        "Vdc_max": 1500,
        "MPPT_vmin": 480, "MPPT_vmax": 1500,
        "Isc_mppt_max": 50,
        "Imp_mppt_max": 30,
        "mppt_count": 15,
        "strings_per_mppt": 2,
        "S_ac_kVA": 352,
        "efficiency_pct": 98.8,
        "derated_rule": "minus10pct",
    },
    "GW350KH-UT": {
        "series": "UT",
        "Vdc_max": 1500,
        "MPPT_vmin": 480, "MPPT_vmax": 1500,
        "Isc_mppt_max": 60,
        "Imp_mppt_max": 40,
        "mppt_count": 12,
        "strings_per_mppt": 2,
        "S_ac_kVA": 352,
        "efficiency_pct": 98.8,
        "derated_rule": "minus10pct",
    },
}

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Inverter Selection")
inv_name = st.sidebar.selectbox("Inverter model", list(INVERTERS.keys()))
inv = INVERTERS[inv_name]

with st.expander("Selected inverter details"):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Series:** {inv['series']}")
        st.write(f"**Vdc max:** {inv['Vdc_max']} V")
        st.write(f"**MPPT window:** {inv['MPPT_vmin']}–{inv['MPPT_vmax']} V")
        st.write(f"**MPPTs:** {inv['mppt_count']}")
    with col2:
        st.write(f"**Strings per MPPT:** {inv['strings_per_mppt']}")
        st.write(f"**Isc max / MPPT:** {inv['Isc_mppt_max']} A")
        st.write(f"**Imp max / MPPT:** {inv['Imp_mppt_max']} A")
        st.write(f"**AC rating:** {inv['S_ac_kVA']} kVA")

st.sidebar.header("Module (STC) & Tempco")
Voc = st.sidebar.number_input("Voc (V)", min_value=0.0, value=52.0, step=0.1)
Vmp = st.sidebar.number_input("Vmp (V)", min_value=0.0, value=44.0, step=0.1)
Isc = st.sidebar.number_input("Isc (A)", min_value=0.0, value=14.0, step=0.1)
Imp = st.sidebar.number_input("Imp (A)", min_value=0.0, value=13.2, step=0.1)

beta_unit = st.sidebar.selectbox("βVoc unit", ["%/°C", "V/°C"])
beta_voc = st.sidebar.number_input("βVoc (enter with selected unit)", value=-0.28, step=0.01)
gamma_pmp = st.sidebar.number_input("γPmp (%/°C)", value=-0.35, step=0.01)
beta_vmp = st.sidebar.number_input("βVmp (%/°C, optional; default -0.30)", value=-0.30, step=0.01)

st.sidebar.header("Temperatures & Safety")
Tmin = st.sidebar.number_input("Minimum ambient temperature (°C)", value=-15.0, step=1.0)
Tmax = st.sidebar.number_input("Hot temperature for Vmp check (°C)", value=60.0, step=1.0)
k_safety = st.sidebar.slider("k_safety (voltage safety factor)", min_value=1.00, max_value=1.10, value=1.05, step=0.01)

# -----------------------------
# Calculations
# -----------------------------
# Voc at Tmin
if beta_unit == "%/°C":
    voc_Tmin = Voc * (1.0 + (beta_voc / 100.0) * (Tmin - 25.0))
else:  # V/°C
    voc_Tmin = Voc + beta_voc * (Tmin - 25.0)

# Max series modules N_max
if voc_Tmin <= 0:
    N_max = 0
else:
    N_max = math.floor(inv["Vdc_max"] / (voc_Tmin * k_safety))
    N_max = max(N_max, 0)

# User chooses series modules with cap N_max
st.subheader("1) Series Module Count (Design Choice)")
if N_max == 0:
    st.error("N_max = 0. Given Tmin and βVoc lead to too high Voc. Please reduce Tmin, k_safety, or use different module/inverter.")
    N_series = 0
else:
    N_series = st.slider("Modules in series per string", min_value=1, max_value=N_max, value=min(N_max, 26))

st.caption(f"Computed N_max = **{N_max}** (from Voc@Tmin={voc_Tmin:.2f} V, Vdc_max={inv['Vdc_max']} V, k_safety={k_safety:.2f})")

# Isc & Imp checks per MPPT (using fixed 'strings_per_mppt' from inverter)
strings_per_mppt = inv["strings_per_mppt"]
Isc_mppt = Isc * strings_per_mppt
Imp_mppt = Imp * strings_per_mppt

# Hot Vmp check (optional): Vmp at Tmax (approx with βVmp)
Vmp_Tmax = Vmp * (1.0 + (beta_vmp / 100.0) * (Tmax - 25.0))
string_Vmp_Tmax = N_series * Vmp_Tmax

# -----------------------------
# Results / Status
# -----------------------------
st.subheader("2) Limit Checks (per MPPT)")

colA, colB = st.columns(2)
with colA:
    st.write("**Cold Voc (module):** {:.2f} V @ {}°C".format(voc_Tmin, Tmin))
    st.write("**String Voc @ Tmin (approx):** {:.2f} V".format(N_series * voc_Tmin))
    if N_series == 0:
        st.warning("No series modules selected.")
    elif N_series == N_max:
        st.info("Series count at the safe maximum (N_max).")
with colB:
    st.write("**MPPT window:** {}–{} V".format(inv["MPPT_vmin"], inv["MPPT_vmax"]))
    st.write("**String Vmp @ Tmax (approx):** {:.2f} V".format(string_Vmp_Tmax))
    if string_Vmp_Tmax < inv["MPPT_vmin"]:
        st.warning("At hot conditions, string Vmp could be below MPPT_min → tracking margin is low. Consider increasing N_series.")

st.write("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Isc safety (STC)**")
    st.write(f"Isc per MPPT = Isc_module × strings/MPPT = **{Isc:.2f} × {strings_per_mppt} = {Isc_mppt:.2f} A**")
    st.write(f"Isc limit / MPPT = **{inv['Isc_mppt_max']} A**")
    if Isc_mppt <= inv["Isc_mppt_max"]:
        st.success("PASS — Isc per MPPT within limit.")
    else:
        st.error("FAIL — Isc per MPPT exceeds limit! Reduce parallel strings or choose different inverter/module.")

with col2:
    st.markdown("**Imp operational (clipping risk)**")
    st.write(f"Imp per MPPT = Imp_module × strings/MPPT = **{Imp:.2f} × {strings_per_mppt} = {Imp_mppt:.2f} A**")
    st.write(f"Imp limit / MPPT = **{inv['Imp_mppt_max']} A**")
    if Imp_mppt <= inv["Imp_mppt_max"]:
        st.success("OK — No current clipping expected from MPPT limit at STC.")
    else:
        st.warning("RISK — Imp exceeds MPPT current limit at STC → DC current clipping will occur in high-irradiance hours (Step 2 will quantify).")

st.write("---")
st.subheader("3) Next")
st.write("Bu adımda seri modül sayısını güvenli sınırlar içinde seçtiniz ve Isc/Imp kontrollerini gördünüz.")
st.write("**Step 2**'de koordinat girişiyle PVGIS verisi üzerinden saatlik üretim ve clipping kayıplarını hesaplayacağız.")