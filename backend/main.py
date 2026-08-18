import os
import sqlite3
import json
import math
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.llm_service import (
    explain_capacity,
    explain_distance,
    explain_total,
    explain_hhi,
    simulate_what_if
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.path.join(str(BASE_DIR), "carenet.db")

app = FastAPI(
    title="CARENET - Healthcare Provider Network Adequacy & Access Intelligence API",
    version="3.2.0",
    description="Healthcare Provider Network Intelligence API powered directly by the 3-Metric Summary Table and Backend Claude AI."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class ExplainRequest(BaseModel):
    county: str
    city: str
    specialty: str
    metric_type: str  # "capacity", "distance", "total"
    metrics: Dict[str, Any]

class WhatIfRequest(BaseModel):
    county: str
    city: str
    specialty: str
    question: str
    base_metrics: Dict[str, Any]

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {
        "system": "CARENET Healthcare Provider Network Intelligence API",
        "status": "online",
        "version": "3.2.0"
    }

@app.get("/api/summary")
def get_summary_statistics():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT AVG(total_adequacy) as avg_tot FROM semantic_adequacy")
    avg_total = cursor.fetchone()["avg_tot"] or 58.4

    cursor.execute("SELECT AVG(capacity_adequacy) as avg_cap FROM semantic_adequacy")
    avg_cap = cursor.fetchone()["avg_cap"] or 55.2

    cursor.execute("SELECT AVG(distance_adequacy) as avg_dist FROM semantic_adequacy")
    avg_dist = cursor.fetchone()["avg_dist"] or 52.8

    conn.close()

    return {
        "average_total_adequacy": round(avg_total, 1),
        "average_capacity_adequacy": round(avg_cap, 1),
        "average_distance_adequacy": round(avg_dist, 1),
        "active_counties": 6,
        "specialties_count": 7
    }

@app.get("/api/counties", response_model=List[str])
def get_counties():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT county FROM semantic_adequacy ORDER BY county")
    counties = [r["county"] for r in cursor.fetchall()]
    conn.close()
    return counties

@app.get("/api/counties/{county}/cities", response_model=List[str])
def get_cities_by_county(county: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM semantic_adequacy WHERE LOWER(county) = LOWER(?) ORDER BY city", (county,))
    cities = [r["city"] for r in cursor.fetchall()]
    conn.close()
    return cities

@app.get("/api/specialties", response_model=List[str])
def get_specialties():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT specialty FROM semantic_adequacy ORDER BY specialty")
    specialties = [r["specialty"] for r in cursor.fetchall()]
    conn.close()
    return specialties

# ----------------------------------------------------------------------------
# 1. GET /api/adequacy & /api/metrics (READS EXACTLY 3 METRICS FROM SUMMARY TABLE)
# ----------------------------------------------------------------------------
@app.get("/metrics")
@app.get("/api/metrics")
@app.get("/api/adequacy")
def get_metrics(
    county: str = Query(..., description="County name e.g. Harris"),
    city: str = Query(..., description="City name e.g. Houston"),
    specialty: str = Query(..., description="Specialty name e.g. Cardiology")
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM semantic_adequacy
        WHERE LOWER(county) = LOWER(?) AND LOWER(city) = LOWER(?) AND LOWER(specialty) = LOWER(?)
    """, (county, city, specialty))
    row = cursor.fetchone()

    cursor.execute("""
        SELECT zip_code, capacity_adequacy, distance_adequacy, total_adequacy, status, latitude, longitude
        FROM zipcode_adequacy
        WHERE LOWER(county) = LOWER(?) AND LOWER(city) = LOWER(?) AND LOWER(specialty) = LOWER(?)
    """, (county, city, specialty))
    zipcode_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not row:
        conn2 = get_db()
        c2 = conn2.cursor()
        c2.execute("SELECT * FROM semantic_adequacy WHERE LOWER(county) = LOWER(?) AND LOWER(specialty) = LOWER(?) LIMIT 1", (county, specialty))
        row = c2.fetchone()
        conn2.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"No precomputed metrics found for {specialty} in {city}, {county} County.")

    data = dict(row)
    data["adequacy_status"] = "GREEN" if data["total_adequacy"] >= 80 else ("YELLOW" if data["total_adequacy"] >= 50 else "RED")
    data["zipcodes"] = zipcode_rows

    return data

# ----------------------------------------------------------------------------
# 2. GET /api/zipcodes
# ----------------------------------------------------------------------------
@app.get("/api/zipcodes")
def get_zipcodes(
    county: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT county, city, specialty, capacity_adequacy, distance_adequacy, total_adequacy, status, zip_code, latitude, longitude FROM zipcode_adequacy WHERE 1=1"
    params = []

    if county:
        query += " AND LOWER(county) = LOWER(?)"
        params.append(county)
    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if specialty:
        query += " AND LOWER(specialty) = LOWER(?)"
        params.append(specialty)

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# ----------------------------------------------------------------------------
# 3. POST /api/explain (BACKEND-PROXIED CLAUDE CALL)
# ----------------------------------------------------------------------------
@app.post("/explain")
@app.post("/api/explain")
def explain_metric(req: ExplainRequest):
    metric_type = req.metric_type.lower()

    if metric_type == "capacity":
        res = explain_capacity(req.county, req.city, req.specialty, req.metrics)
    elif metric_type == "distance":
        res = explain_distance(req.county, req.city, req.specialty, req.metrics)
    else:
        res = explain_total(req.county, req.city, req.specialty, req.metrics)

    res["metric_type"] = metric_type
    return res

# ----------------------------------------------------------------------------
# 4. POST /api/what-if (BACKEND-PROXIED WHAT-IF SIMULATOR)
# ----------------------------------------------------------------------------
@app.post("/what-if")
@app.post("/api/what-if")
def what_if_simulator(req: WhatIfRequest):
    return simulate_what_if(req.county, req.city, req.specialty, req.question, req.base_metrics)

# ----------------------------------------------------------------------------
# 5. GET /api/map-data (MANY SMALL DOTS PER ZIP CODE + ADEQUACY OVERLAYS)
# ----------------------------------------------------------------------------
@app.get("/map-data")
@app.get("/api/map-data")
def get_map_data(
    county: Optional[str] = Query(None, description="Optional county filter"),
    city: Optional[str] = Query(None, description="Optional city filter"),
    specialty: str = Query("Cardiology", description="Specialty name")
):
    conn = get_db()
    cursor = conn.cursor()

    # 1. Query individual providers with spatial distribution
    prov_query = """
        SELECT npi, name, specialty, county, city, zip_code, latitude, longitude, facility_name
        FROM providers
        WHERE LOWER(specialty) = LOWER(?) AND latitude IS NOT NULL AND longitude IS NOT NULL
    """
    prov_params = [specialty]

    if county and county != "All Counties":
        prov_query += " AND LOWER(county) = LOWER(?)"
        prov_params.append(county)
        if city and city != "All Cities":
            prov_query += " AND LOWER(city) = LOWER(?)"
            prov_params.append(city)

    cursor.execute(prov_query + " LIMIT 400", prov_params)
    providers = [dict(r) for r in cursor.fetchall()]

    # 2. Query individual patients distributed across zip codes
    pat_query = """
        SELECT patient_id, specialty, county, city, zip_code, latitude, longitude, age
        FROM patients
        WHERE LOWER(specialty) = LOWER(?) AND latitude IS NOT NULL AND longitude IS NOT NULL
    """
    pat_params = [specialty]

    if county and county != "All Counties":
        pat_query += " AND LOWER(county) = LOWER(?)"
        pat_params.append(county)
        if city and city != "All Cities":
            pat_query += " AND LOWER(city) = LOWER(?)"
            pat_params.append(city)

    cursor.execute(pat_query + " LIMIT 600", pat_params)
    patients = [dict(r) for r in cursor.fetchall()]

    # 3. Heatmap adequacy summaries by city
    cursor.execute("""
        SELECT county, city, total_adequacy, capacity_adequacy, distance_adequacy, status
        FROM semantic_adequacy
        WHERE LOWER(specialty) = LOWER(?)
    """, (specialty,))
    city_summaries = {}
    for r in cursor.fetchall():
        c_item = dict(r)
        tot_ad = c_item["total_adequacy"]
        c_item["adequacy_status"] = "GREEN" if tot_ad >= 80 else ("YELLOW" if tot_ad >= 50 else "RED")
        city_summaries[f"{c_item['county']}_{c_item['city']}"] = c_item

    # 4. Individual ZIP code points with 3-metric adequacy
    zip_query = "SELECT county, city, specialty, capacity_adequacy, distance_adequacy, total_adequacy, status, zip_code, latitude, longitude FROM zipcode_adequacy WHERE LOWER(specialty) = LOWER(?)"
    zip_params = [specialty]
    if county:
        zip_query += " AND LOWER(county) = LOWER(?)"
        zip_params.append(county)
        if city:
            zip_query += " AND LOWER(city) = LOWER(?)"
            zip_params.append(city)

    cursor.execute(zip_query, zip_params)
    zipcodes = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "specialty": specialty,
        "selected_county": county,
        "selected_city": city,
        "providers": providers,
        "patients": patients,
        "city_summaries": city_summaries,
        "zipcodes": zipcodes
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
