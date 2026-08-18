import numpy as np
import pandas as pd

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula"""
    earth_radius_miles = 3958.7613
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    
    a = (np.sin(delta_lat / 2) ** 2 +
         np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2)
    
    c = 2 * np.arcsin(np.sqrt(a))
    return earth_radius_miles * c

def calculate_nearest_provider_distances(patients, providers):
    """Find nearest provider for each patient"""
    patients = patients.copy()
    providers = providers.copy()

    required_patient_columns = ["Patient_ID", "Latitude", "Longitude"]
    required_provider_columns = ["NPI", "Latitude", "Longitude"]

    for column in required_patient_columns:
        if column not in patients.columns:
            raise KeyError(f"Patient column missing: {column}")
    
    for column in required_provider_columns:
        if column not in providers.columns:
            raise KeyError(f"Provider column missing: {column}")

    patients["Latitude"] = pd.to_numeric(patients["Latitude"], errors="coerce")
    patients["Longitude"] = pd.to_numeric(patients["Longitude"], errors="coerce")
    providers["Latitude"] = pd.to_numeric(providers["Latitude"], errors="coerce")
    providers["Longitude"] = pd.to_numeric(providers["Longitude"], errors="coerce")

    patients = patients.dropna(subset=["Latitude", "Longitude"]).copy()
    providers = providers.dropna(subset=["Latitude", "Longitude"]).copy()

    if providers.empty:
        patients["Nearest_Provider_NPI"] = None
        patients["Minimum_Distance_Miles"] = np.nan
        return patients

    provider_latitudes = providers["Latitude"].to_numpy()
    provider_longitudes = providers["Longitude"].to_numpy()
    provider_npis = providers["NPI"].to_numpy()

    minimum_distances = []
    nearest_provider_ids = []

    for _, patient in patients.iterrows():
        patient_lat = patient["Latitude"]
        patient_lon = patient["Longitude"]
        
        distances = haversine_distance(
            patient_lat, patient_lon,
            provider_latitudes, provider_longitudes
        )
        
        minimum_index = np.argmin(distances)
        minimum_distance = distances[minimum_index]
        nearest_provider = provider_npis[minimum_index]
        
        minimum_distances.append(float(minimum_distance))
        nearest_provider_ids.append(nearest_provider)

    patients["Nearest_Provider_NPI"] = nearest_provider_ids
    patients["Minimum_Distance_Miles"] = minimum_distances
    return patients

def calculate_distance_adequacy(patient_distances, maximum_distance):
    """Calculate distance adequacy WITH 100% CAP"""
    if maximum_distance is None:
        raise ValueError("Maximum distance is not available.")
    
    maximum_distance = float(maximum_distance)
    
    if maximum_distance <= 0:
        raise ValueError("Maximum distance must be greater than zero.")
    
    if patient_distances.empty:
        return {
            "total_patients": 0,
            "reasonable_patients": 0,
            "unreasonable_patients": 0,
            "distance_adequacy": 0,
            "maximum_distance": maximum_distance
        }

    sorted_patients = (
        patient_distances
        .sort_values(by="Minimum_Distance_Miles", ascending=True)
        .reset_index(drop=True)
    )

    sorted_patients["Reasonable_Distance"] = (
        sorted_patients["Minimum_Distance_Miles"] <= maximum_distance
    )

    reasonable_patients = int(sorted_patients["Reasonable_Distance"].sum())
    total_patients = len(sorted_patients)
    unreasonable_patients = total_patients - reasonable_patients

    # FIXED: WITH 100% CAP - Never exceeds 100%
    if total_patients == 0:
        adequacy = 0
    else:
        raw_adequacy = (reasonable_patients / total_patients) * 100
        adequacy = min(raw_adequacy, 100)  # ✅ CAPPED AT 100%

    return {
        "total_patients": total_patients,
        "reasonable_patients": reasonable_patients,
        "unreasonable_patients": unreasonable_patients,
        "distance_adequacy": round(adequacy, 2),  # ✅ Max 100%
        "maximum_distance": maximum_distance,
        "patient_distances": sorted_patients
    }