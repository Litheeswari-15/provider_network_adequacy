import math

def calculate_capacity_adequacy(
    provider_count,
    patient_count,
    capacity_per_provider
):
    """
    Calculate capacity adequacy WITH 100% CAP
    Maximum value is 100% - never exceeds this
    """

    provider_count = int(provider_count)
    patient_count = int(patient_count)
    capacity_per_provider = float(capacity_per_provider)

    # Validation
    if provider_count < 0:
        raise ValueError("Provider count cannot be negative.")
    if patient_count < 0:
        raise ValueError("Patient count cannot be negative.")
    if capacity_per_provider <= 0:
        raise ValueError("Capacity per provider must be greater than zero.")

    # Total capacity
    total_capacity = provider_count * capacity_per_provider

    # No patients
    if patient_count == 0:
        return {
            "provider_count": provider_count,
            "patient_count": patient_count,
            "capacity_per_provider": capacity_per_provider,
            "total_capacity": total_capacity,
            "capacity_adequacy": None,
            "capacity_gap": 0,
            "additional_providers": 0,
            "status": "NO PATIENT DEMAND"
        }

    # FIXED: WITH 100% CAP - Never exceeds 100%
    raw_adequacy = (total_capacity / patient_count) * 100
    capacity_adequacy = min(raw_adequacy, 100)  # ✅ CAPPED AT 100%

    # Capacity gap
    if total_capacity >= patient_count:
        capacity_gap = 0
        additional_providers = 0
    else:
        capacity_gap = patient_count - total_capacity
        additional_providers = math.ceil(capacity_gap / capacity_per_provider)

    # Status
    if provider_count == 0:
        status = "NO PROVIDERS"
    elif total_capacity < patient_count:
        status = "CAPACITY GAP"
    else:
        status = "ADEQUATE"

    return {
        "provider_count": provider_count,
        "patient_count": patient_count,
        "capacity_per_provider": capacity_per_provider,
        "total_capacity": total_capacity,
        "capacity_adequacy": round(capacity_adequacy, 2),  # ✅ Max 100%
        "capacity_gap": round(capacity_gap, 2),
        "additional_providers": additional_providers,
        "status": status
    }