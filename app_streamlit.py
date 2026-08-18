import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import requests
import json
import sqlite3
import os
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="CARENET - Healthcare Network Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://localhost:8000"
DB_PATH = Path(__file__).resolve().parent / "backend" / "carenet.db"

# Custom CSS for executive dark theme
st.markdown("""
<style>
    .reportview-container, .main, .block-container {
        background: #0B132B;
        color: #F8FAFC;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .metric-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .badge-green {
        background: rgba(46, 204, 113, 0.2);
        color: #2ECC71;
        padding: 3px 8px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(46, 204, 113, 0.4);
    }
    .badge-yellow {
        background: rgba(241, 196, 15, 0.2);
        color: #F1C40F;
        padding: 3px 8px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(241, 196, 15, 0.4);
    }
    .badge-red {
        background: rgba(255, 118, 117, 0.2);
        color: #FF7675;
        padding: 3px 8px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(255, 118, 117, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Database helper
@st.cache_data
def get_filters_from_db():
    if not DB_PATH.exists():
        return [], {}, []
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT county FROM semantic_adequacy ORDER BY county")
    counties = [r[0] for r in cursor.fetchall()]
    
    cities_by_county = {}
    for c in counties:
        cursor.execute("SELECT DISTINCT city FROM semantic_adequacy WHERE county = ? ORDER BY city", (c,))
        cities_by_county[c] = [r[0] for r in cursor.fetchall()]
        
    cursor.execute("SELECT DISTINCT specialty FROM semantic_adequacy ORDER BY specialty")
    specialties = [r[0] for r in cursor.fetchall()]
    
    conn.close()
    return counties, cities_by_county, specialties

@st.cache_data
def fetch_metrics(county, city, specialty):
    try:
        r = requests.get(f"{API_BASE}/metrics", params={"county": county, "city": city, "specialty": specialty}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    
    # Direct DB fallback
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM semantic_adequacy WHERE LOWER(county)=LOWER(?) AND LOWER(city)=LOWER(?) AND LOWER(specialty)=LOWER(?)", (county, city, specialty))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    return None

@st.cache_data
def fetch_dashboard(county, city):
    try:
        r = requests.get(f"{API_BASE}/dashboard", params={"county": county, "city": city}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

# App Header
st.title("🏥 CARENET")
st.markdown("##### Healthcare Provider Network Adequacy & Access Intelligence Platform")
st.markdown("---")

# Sidebar Cascading Filters
st.sidebar.header("🔍 Network Scope Filters")

counties, cities_by_county, specialties = get_filters_from_db()

selected_county = st.sidebar.selectbox("1. Select County", options=[""] + counties, index=0)

if selected_county:
    available_cities = cities_by_county.get(selected_county, [])
    selected_city = st.sidebar.selectbox("2. Select City", options=[""] + available_cities, index=0)
else:
    selected_city = st.sidebar.selectbox("2. Select City", options=["Select County First"], disabled=True)

if selected_county and selected_city and selected_city != "Select County First":
    selected_specialty = st.sidebar.selectbox("3. Select Specialty", options=[""] + specialties, index=0)
else:
    selected_specialty = st.sidebar.selectbox("3. Select Specialty", options=["Select City First"], disabled=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Single Source of Truth**: All adequacy metrics are queried directly from `semantic_adequacy` (`semantic_table.csv`). Market HHI is calculated dynamically on runtime.")

# Main Interface Content
if not selected_county or not selected_city or not selected_specialty or selected_city == "Select County First" or selected_specialty == "Select City First":
    st.info("👋 **Welcome to CARENET**: Please select a **County**, **City**, and **Medical Specialty** from the sidebar to view network adequacy metrics, interactive maps, and AI insights.")
else:
    metrics = fetch_metrics(selected_county, selected_city, selected_specialty)
    
    if not metrics:
        st.error(f"No semantic record found for {selected_specialty} in {selected_city}, {selected_county} County.")
    else:
        # Four Metric Cards
        tot_adeq = round(float(metrics.get("total_adequacy", 0.0)), 1)
        cap_adeq = round(float(metrics.get("capacity_adequacy", 0.0)), 1)
        dist_adeq = round(float(metrics.get("distance_adequacy", 0.0)), 1)
        cap_gap = round(float(metrics.get("capacity_gap", 0.0)), 1)
        market_hhi = round(float(metrics.get("market_hhi", 0.0)), 1)
        hhi_interp = metrics.get("hhi_interpretation", "BALANCED")
        needed_docs = int(metrics.get("additional_providers_needed", 0))
        pat_count = int(metrics.get("patient_count", 0))
        prov_count = int(metrics.get("provider_count", 0))
        
        status_color = "badge-green" if tot_adeq > 80 else ("badge-yellow" if tot_adeq >= 50 else "badge-red")
        status_label = "HIGHLY ADEQUATE" if tot_adeq > 80 else ("PARTIALLY ADEQUATE" if tot_adeq >= 50 else "CRITICAL SHORTAGE")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid {'#2ECC71' if tot_adeq > 80 else ('#F1C40F' if tot_adeq >= 50 else '#FF7675')};">
                <div class="metric-title">1. Total Adequacy</div>
                <div class="metric-value">{tot_adeq}%</div>
                <div style="margin-top: 8px;"><span class="{status_color}">{status_label}</span></div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 6px;">Composite Index</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🤖 Explain Total", key="btn_exp_total"):
                with st.spinner("Calling Claude AI..."):
                    res = requests.post(f"{API_BASE}/api/explain", json={
                        "county": selected_county, "city": selected_city, "specialty": selected_specialty,
                        "metric_type": "total", "metrics": metrics
                    })
                    if res.status_code == 200:
                        st.markdown(res.json().get("explanation", ""))

        with c2:
            st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #38BDF8;">
                <div class="metric-title">2. Capacity Adequacy</div>
                <div class="metric-value" style="color: #38BDF8;">{cap_adeq}%</div>
                <div style="font-size: 0.8rem; color: #F1C40F; margin-top: 8px;"><b>Gap:</b> {cap_gap}% | <b>Shortage:</b> +{needed_docs} docs</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">{prov_count} active docs / {pat_count} demand</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🤖 Explain Capacity", key="btn_exp_cap"):
                with st.spinner("Calling Claude AI..."):
                    res = requests.post(f"{API_BASE}/api/explain", json={
                        "county": selected_county, "city": selected_city, "specialty": selected_specialty,
                        "metric_type": "capacity", "metrics": metrics
                    })
                    if res.status_code == 200:
                        st.markdown(res.json().get("explanation", ""))

        with c3:
            st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #A78BFA;">
                <div class="metric-title">3. Distance Adequacy</div>
                <div class="metric-value" style="color: #A78BFA;">{dist_adeq}%</div>
                <div style="font-size: 0.8rem; color: #2ECC71; margin-top: 8px;"><b>Access:</b> {metrics.get('reasonable_patients', 0)} patients</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">≤{int(metrics.get('maximum_distance', 45))} min threshold</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🤖 Explain Distance", key="btn_exp_dist"):
                with st.spinner("Calling Claude AI..."):
                    res = requests.post(f"{API_BASE}/api/explain", json={
                        "county": selected_county, "city": selected_city, "specialty": selected_specialty,
                        "metric_type": "distance", "metrics": metrics
                    })
                    if res.status_code == 200:
                        st.markdown(res.json().get("explanation", ""))

        with c4:
            st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #F59E0B;">
                <div class="metric-title">4. Market HHI (Dynamic)</div>
                <div class="metric-value" style="color: #F59E0B;">{market_hhi}</div>
                <div style="font-size: 0.8rem; color: #F8FAFC; margin-top: 8px;"><b>Structure:</b> {hhi_interp}</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Top: {metrics.get('top_provider_name', 'Independent')[:20]} ({metrics.get('top_provider_share', 0)}%)</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🤖 Explain Market", key="btn_exp_hhi"):
                with st.spinner("Calling Claude AI..."):
                    res = requests.post(f"{API_BASE}/api/explain", json={
                        "county": selected_county, "city": selected_city, "specialty": selected_specialty,
                        "metric_type": "hhi", "metrics": metrics
                    })
                    if res.status_code == 200:
                        st.markdown(res.json().get("explanation", ""))

        st.markdown("---")

        # Map Visualization & Heatmap
        st.subheader(f"🗺️ Geospatial Network Map & Heatmap ({selected_specialty})")
        
        # Coordinate map dictionary
        CITY_COORDS = {
            "Houston": (29.7604, -95.3698), "Dallas": (32.7767, -96.7970), "San Antonio": (29.4241, -98.4936),
            "Austin": (30.2672, -97.7431), "Fort Worth": (32.7555, -97.3308), "Plano": (33.0198, -96.6989),
            "Arlington": (32.7357, -97.1081), "Irving": (32.8140, -96.9489), "Frisco": (33.1507, -96.8236),
            "Baytown": (29.7355, -94.9774), "Bellaire": (29.7058, -95.4588), "Lakeway": (30.3644, -97.9814),
            "Pflugerville": (30.4548, -97.6223), "Boerne": (29.7947, -98.7320), "Keller": (32.9342, -97.2295),
            "Cedar Hill": (32.5885, -96.9561), "Humble": (29.9988, -95.2622), "Pasadena": (29.6911, -95.2091)
        }

        # Query all cities for heatmap in this specialty
        conn = sqlite3.connect(str(DB_PATH))
        df_cities = pd.read_sql_query("SELECT city, total_adequacy, capacity_adequacy, distance_adequacy, status FROM semantic_adequacy WHERE LOWER(specialty)=LOWER(?)", conn, params=(selected_specialty,))
        conn.close()

        map_rows = []
        for _, r in df_cities.iterrows():
            c_name = r["city"]
            tot = float(r["total_adequacy"])
            if c_name in CITY_COORDS:
                lat, lon = CITY_COORDS[c_name]
                # Heatmap rule: Green > 80, Yellow 50-80, Red < 50
                color = [46, 204, 113, 200] if tot > 80 else ([241, 196, 15, 200] if tot >= 50 else [255, 118, 117, 200])
                map_rows.append({
                    "city": c_name, "latitude": lat, "longitude": lon,
                    "total_adequacy": tot, "status": r["status"],
                    "color": color, "radius": 15000 if tot > 80 else 10000
                })

        if map_rows:
            df_map = pd.DataFrame(map_rows)
            view_lat, view_lon = CITY_COORDS.get(selected_city, (31.0, -97.5))
            
            deck = pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=pdk.ViewState(latitude=view_lat, longitude=view_lon, zoom=7, pitch=35),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=df_map,
                        get_position=["longitude", "latitude"],
                        get_color="color",
                        get_radius="radius",
                        pickable=True,
                        auto_highlight=True
                    ),
                    pdk.Layer(
                        "TextLayer",
                        data=df_map,
                        get_position=["longitude", "latitude"],
                        get_text="city",
                        get_color=[255, 255, 255, 255],
                        get_size=13,
                        get_alignment_baseline="'bottom'"
                    )
                ],
                tooltip={"html": "<b>{city}</b><br/>Total Adequacy: {total_adequacy}%<br/>Status: {status}", "style": {"color": "white"}}
            )
            st.pydeck_chart(deck)

        st.markdown("---")

        # All Specialties Comparative Matrix
        st.subheader(f"📊 All-Specialties Adequacy Table ({selected_city}, {selected_county} County)")
        dash_data = fetch_dashboard(selected_county, selected_city)
        if dash_data:
            df_table = pd.DataFrame(dash_data)[[
                "specialty", "total_adequacy", "capacity_adequacy", "distance_adequacy", "capacity_gap", "additional_providers_needed", "market_hhi", "hhi_interpretation", "status"
            ]]
            df_table.columns = ["Specialty", "Total Adequacy (%)", "Capacity (%)", "Distance (%)", "Capacity Gap (%)", "Docs Needed", "Market HHI", "HHI Structure", "Compliance Status"]
            st.dataframe(df_table, use_container_width=True, hide_index=True)

        st.markdown("---")

        # What-If Simulator
        st.subheader("🔮 AI What-If Scenario Simulator")
        st.markdown("Model interventions such as recruiting specialists, launching satellite clinics, or adjusting contract networks.")
        
        user_query = st.text_input(
            "Enter your scenario proposal:",
            value=f"If we recruit 5 additional {selected_specialty.lower()} specialists in {selected_city}, what is the projected impact on Total Adequacy and Market HHI?"
        )

        if st.button("🚀 Run Scenario Simulation", key="btn_run_whatif"):
            with st.spinner("Evaluating counterfactual scenario with Claude AI..."):
                res = requests.post(f"{API_BASE}/api/what-if", json={
                    "county": selected_county,
                    "city": selected_city,
                    "specialty": selected_specialty,
                    "question": user_query,
                    "base_metrics": metrics
                })
                if res.status_code == 200:
                    sim_data = res.json()
                    st.success("Simulation Complete")
                    st.markdown(sim_data.get("response", ""))
                else:
                    st.error("Failed to run What-If simulation. Please verify backend connection.")
