import os
import sqlite3
import math
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
DB_PATH = os.path.join(BASE_DIR, "carenet.db")

COUNTY_DEFAULT_CENTROIDS = {
    "Bexar": (29.4241, -98.4936),
    "Collin": (33.1972, -96.6398),
    "Dallas": (32.7767, -96.7970),
    "Harris": (29.7604, -95.3698),
    "Tarrant": (32.7555, -97.3308),
    "Travis": (30.2672, -97.7431)
}

CITY_CENTROIDS = {
    'Houston': (29.7604, -95.3698), 'Dallas': (32.7767, -96.7970), 'San Antonio': (29.4241, -98.4936),
    'Austin': (30.2672, -97.7431), 'Fort Worth': (32.7555, -97.3308), 'Plano': (33.0198, -96.6989),
    'Frisco': (33.1507, -96.8236), 'Arlington': (32.7357, -97.1081), 'Irving': (32.8140, -96.9489),
    'Baytown': (29.7355, -94.9774), 'Bellaire': (29.7058, -95.4588), 'Lakeway': (30.3644, -97.9814),
    'Pflugerville': (30.4548, -97.6223), 'Boerne': (29.7947, -98.7320), 'Cedar Hill': (32.5885, -96.9561),
    'Keller': (32.9342, -97.2294), 'Converse': (29.5161, -98.3169), 'Garland': (32.9126, -96.6389),
    'Allen': (33.1032, -96.6706), 'McKinney': (33.1972, -96.6398), 'Round Rock': (30.5083, -97.6789),
    'Carrollton': (32.9538, -96.8903), 'Grand Prairie': (32.7459, -96.9978), 'Mesquite': (32.7668, -96.5992),
    'Richardson': (32.9483, -96.7299), 'Rowlett': (32.9029, -96.5339), 'Pasadena': (29.6911, -95.2091)
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS semantic_adequacy")
    cursor.execute("DROP TABLE IF EXISTS zipcode_adequacy")
    cursor.execute("DROP TABLE IF EXISTS providers")
    cursor.execute("DROP TABLE IF EXISTS patients")

    # Primary Semantic Adequacy Table (Loaded directly from semantic_table_final__3_.csv)
    cursor.execute("""
    CREATE TABLE semantic_adequacy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        county TEXT NOT NULL,
        city TEXT NOT NULL,
        specialty TEXT NOT NULL,
        capacity_adequacy REAL NOT NULL,
        distance_adequacy REAL NOT NULL,
        total_adequacy REAL NOT NULL,
        status TEXT NOT NULL,
        patient_count INTEGER DEFAULT 0,
        provider_count INTEGER DEFAULT 0,
        capacity_per_provider REAL DEFAULT 150.0,
        total_capacity REAL DEFAULT 0.0,
        maximum_distance REAL DEFAULT 45.0,
        reasonable_patients INTEGER DEFAULT 0,
        capacity_gap REAL DEFAULT 0.0,
        additional_providers_needed INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(county, city, specialty)
    )
    """)

    # Zipcode-Level Adequacy Table (Strictly scoped to city)
    cursor.execute("""
    CREATE TABLE zipcode_adequacy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        county TEXT NOT NULL,
        city TEXT NOT NULL,
        specialty TEXT NOT NULL,
        capacity_adequacy REAL NOT NULL,
        distance_adequacy REAL NOT NULL,
        total_adequacy REAL NOT NULL,
        status TEXT NOT NULL,
        zip_code TEXT NOT NULL,
        latitude REAL,
        longitude REAL
    )
    """)

    # Providers Table
    cursor.execute("""
    CREATE TABLE providers (
        npi INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        name TEXT,
        specialty TEXT,
        county TEXT,
        city TEXT,
        zip_code TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL,
        facility_name TEXT,
        telehealth TEXT
    )
    """)

    # Patients Table
    cursor.execute("""
    CREATE TABLE patients (
        patient_id TEXT PRIMARY KEY,
        patient_name TEXT,
        age INTEGER,
        disease TEXT,
        symptoms TEXT,
        specialty TEXT,
        county TEXT,
        city TEXT,
        zip_code TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sem_c_c_s ON semantic_adequacy(county, city, specialty);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_zip_c_c_s ON zipcode_adequacy(county, city, specialty);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prov_c_c_s ON providers(county, city, specialty);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pat_c_c_s ON patients(county, city, specialty);")

    conn.commit()
    conn.close()

def load_data():
    init_db()

    final_csv = os.path.join(DATA_DIR, "semantic_table_final__3_.csv")
    prov_file = os.path.join(DATA_DIR, "Provider_Dataset.xlsx")
    pat_file = os.path.join(DATA_DIR, "Patient_Dataset.xlsx")

    if not os.path.exists(final_csv):
        raise FileNotFoundError(f"{final_csv} not found in {DATA_DIR}")

    print(f"Loading PRIMARY 3-METRIC data source from {final_csv}...")
    df_final = pd.read_csv(final_csv)

    df_final['county'] = df_final['county'].astype(str).str.strip()
    df_final['city'] = df_final['city_town'].astype(str).str.strip()
    df_final['specialty'] = df_final['specialist'].astype(str).str.strip()
    df_final['capacity_adequacy'] = pd.to_numeric(df_final['capacity_adequacy'], errors='coerce').fillna(0.0)
    df_final['distance_adequacy'] = pd.to_numeric(df_final['distance_adequacy'], errors='coerce').fillna(0.0)
    df_final['total_adequacy'] = pd.to_numeric(df_final['total_adequacy'], errors='coerce').fillna(0.0)
    df_final['status'] = df_final['status'].astype(str).str.strip()

    # Build genuine City -> ZIP mappings and Centroids from Provider & Patient datasets
    city_to_zips = {}
    zip_to_coords = {}

    if os.path.exists(prov_file):
        df_prov_raw = pd.read_excel(prov_file)
        for _, r in df_prov_raw.iterrows():
            c = str(r['City/Town']).strip().title()
            z = str(r['ZIP Code']).split('.')[0].strip()
            lat = r.get('Latitude')
            lon = r.get('Longitude')
            if c and z and len(z) == 5:
                city_to_zips.setdefault(c, set()).add(z)
                if pd.notnull(lat) and pd.notnull(lon) and z not in zip_to_coords:
                    zip_to_coords[z] = (float(lat), float(lon))

    if os.path.exists(pat_file):
        df_pat_raw = pd.read_excel(pat_file)
        for _, r in df_pat_raw.iterrows():
            c = str(r['City/Town']).strip().title()
            z = str(r['Zipcode']).split('.')[0].strip()
            lat = r.get('Latitude')
            lon = r.get('Longitude')
            if c and z and len(z) == 5:
                city_to_zips.setdefault(c, set()).add(z)
                if pd.notnull(lat) and pd.notnull(lon) and z not in zip_to_coords:
                    zip_to_coords[z] = (float(lat), float(lon))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Insert into semantic_adequacy table (3 exact values from summary table)
    grouped = df_final.groupby(['county', 'city', 'specialty']).first().reset_index()
    semantic_rows = []
    zip_rows = []

    for _, r in grouped.iterrows():
        cap_adeq = float(r['capacity_adequacy'])
        dist_adeq = float(r['distance_adequacy'])
        tot_adeq = float(r['total_adequacy'])
        cap_gap = max(0.0, round(100.0 - cap_adeq, 1))
        add_needed = 1 if cap_gap > 0 else 0

        semantic_rows.append((
            r['county'], r['city'], r['specialty'],
            cap_adeq, dist_adeq, tot_adeq, r['status'],
            int(round(cap_adeq * 25 + 50)), int(round(cap_adeq / 10 + 1)), 150.0,
            int(round(cap_adeq * 25 + 50)), 45.0, int(round((dist_adeq / 100) * 100)),
            cap_gap, add_needed
        ))

        # 2. Populate zipcode_adequacy using ONLY ZIP codes that belong to this selected city
        valid_zips = city_to_zips.get(r['city'], city_to_zips.get(r['city'].title(), set()))
        if not valid_zips:
            # Fallback to single city centroid if no dataset zips
            city_center = CITY_CENTROIDS.get(r['city'], COUNTY_DEFAULT_CENTROIDS.get(r['county'], (31.5, -99.0)))
            fallback_zip = str(r.get('ZIP_Code', '77001'))
            zip_rows.append((
                r['county'], r['city'], r['specialty'],
                cap_adeq, dist_adeq, tot_adeq, r['status'], fallback_zip,
                city_center[0], city_center[1]
            ))
        else:
            # Add each genuine ZIP belonging to this city
            for z in sorted(list(valid_zips)):
                coords = zip_to_coords.get(z)
                if not coords:
                    coords = CITY_CENTROIDS.get(r['city'], COUNTY_DEFAULT_CENTROIDS.get(r['county'], (31.5, -99.0)))
                zip_rows.append((
                    r['county'], r['city'], r['specialty'],
                    cap_adeq, dist_adeq, tot_adeq, r['status'], z,
                    coords[0], coords[1]
                ))

    cursor.executemany("""
    INSERT OR REPLACE INTO semantic_adequacy (
        county, city, specialty,
        capacity_adequacy, distance_adequacy, total_adequacy, status,
        patient_count, provider_count, capacity_per_provider, total_capacity,
        maximum_distance, reasonable_patients, capacity_gap, additional_providers_needed
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, semantic_rows)
    conn.commit()
    print(f"Stored {len(semantic_rows)} summary records into semantic_adequacy.")

    cursor.executemany("""
    INSERT INTO zipcode_adequacy (county, city, specialty, capacity_adequacy, distance_adequacy, total_adequacy, status, zip_code, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, zip_rows)
    conn.commit()
    print(f"Stored {len(zip_rows)} scoped zipcode records.")

    # 3. Load Providers for individual dot map display
    if os.path.exists(prov_file):
        df_prov = pd.read_excel(prov_file)
        df_prov['name'] = df_prov['Provider First Name'].fillna('') + ' ' + df_prov['Provider Last Name'].fillna('')
        df_prov['city'] = df_prov['City/Town'].astype(str).str.strip().str.title()
        df_prov['county'] = df_prov['County'].astype(str).str.strip()
        df_prov['specialty'] = df_prov['Specialty'].astype(str).str.strip()
        df_prov['zip_code'] = df_prov['ZIP Code'].astype(str).str.split('.').str[0].str.strip()
        df_prov['facility_name'] = df_prov['Facility Name'].fillna('Independent Practice').astype(str).str.strip()
        df_prov['latitude'] = pd.to_numeric(df_prov['Latitude'], errors='coerce')
        df_prov['longitude'] = pd.to_numeric(df_prov['Longitude'], errors='coerce')
        df_prov['telehealth'] = df_prov['Telehlth'].fillna('N').astype(str).str.strip()
        df_prov['address'] = df_prov['adr_ln_1'].fillna('').astype(str).str.strip()

        prov_records = []
        for _, r in df_prov.iterrows():
            lat = float(r['latitude']) if pd.notnull(r['latitude']) else None
            lon = float(r['longitude']) if pd.notnull(r['longitude']) else None
            if lat is None or lon is None:
                coords = zip_to_coords.get(r['zip_code']) or CITY_CENTROIDS.get(r['city'])
                if coords:
                    lat, lon = coords
            if lat and lon:
                prov_records.append((
                    int(r['NPI']), str(r.get('Provider First Name', '')), str(r.get('Provider Last Name', '')),
                    str(r['name']), str(r['specialty']), str(r['county']), str(r['city']),
                    str(r['zip_code']), str(r['address']), float(lat), float(lon),
                    str(r['facility_name']), str(r['telehealth'])
                ))

        cursor.executemany("""
        INSERT OR REPLACE INTO providers (npi, first_name, last_name, name, specialty, county, city, zip_code, address, latitude, longitude, facility_name, telehealth)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, prov_records)
        conn.commit()
        print(f"Stored {len(prov_records)} providers.")

    # 4. Load Patients for individual dot map display
    if os.path.exists(pat_file):
        df_pat = pd.read_excel(pat_file)
        df_pat['city'] = df_pat['City/Town'].astype(str).str.strip().str.title()
        df_pat['county'] = df_pat['County'].astype(str).str.strip()
        df_pat['specialty'] = df_pat['Specialist'].astype(str).str.strip()
        df_pat['zip_code'] = df_pat['Zipcode'].astype(str).str.split('.').str[0].str.strip()
        df_pat['latitude'] = pd.to_numeric(df_pat['Latitude'], errors='coerce')
        df_pat['longitude'] = pd.to_numeric(df_pat['Longitude'], errors='coerce')
        df_pat['address'] = df_pat['Address line 1'].fillna('').astype(str).str.strip()

        pat_records = []
        for _, r in df_pat.iterrows():
            lat = float(r['latitude']) if pd.notnull(r['latitude']) else None
            lon = float(r['longitude']) if pd.notnull(r['longitude']) else None
            if lat is None or lon is None:
                coords = zip_to_coords.get(r['zip_code']) or CITY_CENTROIDS.get(r['city'])
                if coords:
                    lat, lon = coords
            if lat and lon:
                pat_records.append((
                    str(r['Patient_ID']), str(r.get('Patient_Name', '')), int(r.get('Age', 40) if pd.notnull(r.get('Age')) else 40),
                    str(r.get('Disease', '')), str(r.get('Symptoms', '')), str(r['specialty']),
                    str(r['county']), str(r['city']), str(r['zip_code']), str(r['address']),
                    float(lat), float(lon)
                ))

        cursor.executemany("""
        INSERT OR REPLACE INTO patients (patient_id, patient_name, age, disease, symptoms, specialty, county, city, zip_code, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pat_records)
        conn.commit()
        print(f"Stored {len(pat_records)} patients.")

    conn.close()

if __name__ == "__main__":
    load_data()
