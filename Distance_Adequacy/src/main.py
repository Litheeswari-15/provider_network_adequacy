import sys
import os

# FIXED: Update paths to work from Distance_Adequacy directory
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "src"
    )
)

from data_loader import (
    load_patient_data,
    load_provider_data,
    load_distance_rules
)

from distance_calculation import (
    calculate_nearest_provider_distances,
    calculate_distance_adequacy
)

from distance_lookup import (
    get_maximum_distance
)


# =========================================================
# DISPLAY AVAILABLE OPTIONS
# =========================================================

def display_dataset_info(patients, providers):

    print(
        "\n"
        + "-" * 55
    )

    print(
        "AVAILABLE OPTIONS FROM DATASET"
    )

    print(
        "-" * 55
    )

    # Counties
    counties = sorted(
        set(
            patients["County"].unique().tolist() +
            providers["County"].unique().tolist()
        )
    )

    print(
        f"\nCounties ({len(counties)}):"
    )

    for county in counties[:10]:  # Show first 10
        print(f"  • {county}")

    if len(counties) > 10:
        print(f"  ... and {len(counties) - 10} more")

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
        "           DISTANCE ADEQUACY RESULT"
    )

    print(
        "=" * 60
    )

    print(
        f"Total Patients                : "
        f"{result['total_patients']}"
    )

    print(
        f"Patients with Reasonable      : "
        f"Distance {result['reasonable_distance_patients']}"
    )

    print(
        f"Maximum Allowed Distance      : "
        f"{result['maximum_distance']} miles"
    )

    print(
        f"Distance Adequacy             : "
        f"{result['distance_adequacy']}%"
    )

    print(
        f"Status                        : "
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
        "         DISTANCE ADEQUACY ANALYSIS"
    )

    print(
        "=" * 60
    )

    # -------------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------------

    try:

        patients = load_patient_data()

        providers = load_provider_data()

        distance_rules = load_distance_rules()

    except Exception as error:

        print(
            "\n❌ DATA LOADING ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # DISPLAY AVAILABLE OPTIONS
    # -------------------------------------------------------

    display_dataset_info(patients, providers)

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
    # FILTER PATIENTS (FIXED: County instead of State)
    # -------------------------------------------------------

    try:

        # FIXED: Changed from "State" to "County"
        filtered_patients = patients[
            (patients["County"].astype(str).str.upper() == county.upper())
        ]

        # FIXED: Handle "All" city option
        if city.upper() != "ALL":
            filtered_patients = filtered_patients[
                filtered_patients["City/Town"].astype(str).str.contains(
                    city.upper(),
                    na=False,
                    regex=False
                )
            ]
        # If city == "All", no city filter applied (include all cities)

        filtered_patients = filtered_patients[
            filtered_patients["Specialist"].astype(str).str.contains(
                specialty.upper(),
                na=False,
                regex=False
            )
        ]

    except Exception as error:

        print(
            "\n❌ PATIENT FILTER ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # FILTER PROVIDERS (FIXED: County instead of State)
    # -------------------------------------------------------

    try:

        # FIXED: Changed from "State" to "County"
        filtered_providers = providers[
            (providers["County"].astype(str).str.upper() == county.upper())
        ]

        # FIXED: Handle "All" city option
        if city.upper() != "ALL":
            filtered_providers = filtered_providers[
                filtered_providers["City/Town"].astype(str).str.contains(
                    city.upper(),
                    na=False,
                    regex=False
                )
            ]
        # If city == "All", no city filter applied (include all cities)

        filtered_providers = filtered_providers[
            filtered_providers["Specialty"].astype(str).str.contains(
                specialty.upper(),
                na=False,
                regex=False
            )
        ]

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
    # GET MAXIMUM DISTANCE
    # -------------------------------------------------------

    try:

        maximum_distance = get_maximum_distance(
            distance_rules,
            county,
            city,
            specialty
        )

        print(
            f"Maximum distance: {maximum_distance} miles"
        )

    except Exception as error:

        print(
            "\n❌ DISTANCE LOOKUP ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # CALCULATE DISTANCES
    # -------------------------------------------------------

    try:

        patient_distances = (
            calculate_nearest_provider_distances(
                filtered_patients,
                filtered_providers
            )
        )

    except Exception as error:

        print(
            "\n❌ DISTANCE CALCULATION ERROR"
        )

        print(error)

        return

    # -------------------------------------------------------
    # CALCULATE ADEQUACY
    # -------------------------------------------------------

    try:

        result = calculate_distance_adequacy(
            patient_distances,
            maximum_distance
        )

    except Exception as error:

        print(
            "\n❌ ADEQUACY CALCULATION ERROR"
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
    