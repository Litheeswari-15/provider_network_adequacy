import json
import os


from data_loader import (
    load_patient_data,
    load_provider_data
)


from filtering import (
    filter_patients,
    filter_providers
)


from capacity_calculation import (
    calculate_capacity_adequacy
)


# =========================================================
# CONFIG PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "..",
    "config",
    "capacity_config.json"
)


# =========================================================
# LOAD SPECIALTY CAPACITY FROM CONFIG
# =========================================================

def load_specialty_capacities():
    """Load capacity values for each specialty from config"""

    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Config file not found:\n{CONFIG_FILE}"
        )

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    if "specialty_capacity" not in config:
        raise KeyError(
            "specialty_capacity key not found in config"
        )

    return config["specialty_capacity"]


# =========================================================
# GET CAPACITY FOR SPECIFIC SPECIALTY
# =========================================================

def get_capacity_for_specialty(specialty, specialty_capacities):
    """Get capacity per provider for the selected specialty"""

    # Normalize specialty name
    specialty_normalized = specialty.strip().lower()

    # Search in config
    for spec_name, capacity_value in specialty_capacities.items():

        if spec_name.strip().lower() == specialty_normalized:
            return float(capacity_value)

    # If not found, raise error
    raise ValueError(
        f"Specialty '{specialty}' not found in config.\n"
        f"Available specialties: {', '.join(specialty_capacities.keys())}"
    )


# =========================================================
# DISPLAY AVAILABLE SPECIALTIES
# =========================================================

def display_available_specialties(specialty_capacities):

    print(
        "\n"
        + "-" * 55
    )

    print(
        "AVAILABLE SPECIALTIES AND CAPACITIES"
    )

    print(
        "-" * 55
    )

    for specialty, capacity in specialty_capacities.items():

        print(
            f"{specialty:<30} : {capacity} patients per provider"
        )

    print(
        "-" * 55
    )


# =========================================================
# DISPLAY RESULT
# =========================================================

def display_result(result):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "              CAPACITY ADEQUACY RESULT"
    )

    print(
        "=" * 60
    )

    print(
        f"Patient Count             : "
        f"{result['patient_count']}"
    )

    print(
        f"Provider Count            : "
        f"{result['provider_count']}"
    )

    print(
        f"Capacity / Provider       : "
        f"{result['capacity_per_provider']}"
    )

    print(
        f"Total Provider Capacity   : "
        f"{result['total_capacity']}"
    )

    if result["capacity_adequacy"] is None:

        print(
            "Capacity Adequacy         : N/A"
        )

    else:

        print(
            f"Capacity Adequacy         : "
            f"{result['capacity_adequacy']}%"
        )

    print(
        f"Capacity Gap              : "
        f"{result['capacity_gap']}"
    )

    print(
        f"Additional Providers      : "
        f"{result['additional_providers']}"
    )

    print(
        f"Status                    : "
        f"{result['status']}"
    )

    print(
        "=" * 60
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "             CAPACITY ADEQUACY ANALYSIS"
    )

    print(
        "=" * 60
    )

    # -------------------------------------------------------
    # LOAD CONFIG AND SPECIALTY CAPACITIES
    # -------------------------------------------------------

    try:

        specialty_capacities = load_specialty_capacities()

        print(
            f"\n✓ Loaded {len(specialty_capacities)} specialties from config"
        )

    except Exception as error:

        print(
            "\n❌ CONFIG LOADING ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------------

    try:

        patients = load_patient_data()

        providers = load_provider_data()

    except Exception as error:

        print(
            "\n❌ DATA LOADING ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # DISPLAY AVAILABLE SPECIALTIES
    # -------------------------------------------------------

    display_available_specialties(specialty_capacities)

    # -------------------------------------------------------
    # USER INPUTS: COUNTY / CITY / SPECIALTY
    # -------------------------------------------------------

    print(
        "\n"
        + "-" * 55
    )

    print(
        "NETWORK FILTER"
    )

    print(
        "-" * 55
    )

    county = input(
        "Enter County: "
    ).strip()

    city = input(
        "Enter City/Town (or 'All' for all cities): "
    ).strip()

    specialty = input(
        "Enter Specialty: "
    ).strip()

    # -------------------------------------------------------
    # GET CAPACITY FOR THIS SPECIALTY
    # -------------------------------------------------------

    try:

        capacity_per_provider = get_capacity_for_specialty(
            specialty,
            specialty_capacities
        )

        print(
            f"\n✓ Using capacity for {specialty}: "
            f"{capacity_per_provider} patients per provider"
        )

    except ValueError as error:

        print(
            f"\n❌ ERROR: {error}"
        )

        return

    # -------------------------------------------------------
    # FILTER PATIENTS
    # -------------------------------------------------------

    try:

        filtered_patients = filter_patients(
            patients,
            county,
            city,
            specialty
        )

    except Exception as error:

        print(
            "\n❌ PATIENT FILTER ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # FILTER PROVIDERS
    # -------------------------------------------------------

    try:

        filtered_providers = filter_providers(
            providers,
            county,
            city,
            specialty
        )

    except Exception as error:

        print(
            "\n❌ PROVIDER FILTER ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # COUNTS
    # -------------------------------------------------------

    patient_count = len(filtered_patients)

    provider_count = len(filtered_providers)

    print(
        "\n"
        + "-" * 55
    )

    print(
        f"Patients found  : {patient_count}"
    )

    print(
        f"Providers found : {provider_count}"
    )

    # -------------------------------------------------------
    # CALCULATE
    # -------------------------------------------------------

    try:

        result = calculate_capacity_adequacy(
            provider_count=provider_count,
            patient_count=patient_count,
            capacity_per_provider=capacity_per_provider
        )

    except Exception as error:

        print(
            "\n❌ CAPACITY CALCULATION ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------

    display_result(result)


# =========================================================
# RUN PROGRAM
# =========================================================

if __name__ == "__main__":

    main()
