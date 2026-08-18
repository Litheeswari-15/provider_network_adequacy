# =========================================================
# TOTAL ADEQUACY ANALYSIS
# =========================================================

import sys
import os


# =========================================================
# ADD CAPACITY_ADEQUACY SRC TO PYTHON PATH
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


CAPACITY_SRC = os.path.join(
    PROJECT_DIR,
    "Capacity_Adequacy",
    "src"
)


DISTANCE_SRC = os.path.join(
    PROJECT_DIR,
    "Distance_Adequacy",
    "src"
)


sys.path.insert(
    0,
    CAPACITY_SRC
)

sys.path.insert(
    0,
    DISTANCE_SRC
)


# =========================================================
# IMPORT CAPACITY MODULES
# =========================================================

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
# IMPORT DISTANCE MODULES
# =========================================================

from distance_lookup import (
    get_maximum_distance
)

from distance_calculation import (
    calculate_nearest_provider_distances,
    calculate_distance_adequacy
)


# =========================================================
# IMPORTANT
# =========================================================
#
# Because both Capacity_Adequacy and Distance_Adequacy
# contain files named data_loader.py, filtering.py, etc.,
# Python may import the wrong module.
#
# Therefore we will directly load the distance modules
# using unique module names.
# =========================================================

import importlib.util


def load_module(
    module_name,
    file_path
):

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path
    )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


# =========================================================
# LOAD DISTANCE MODULES EXPLICITLY
# =========================================================

distance_loader = load_module(

    "distance_data_loader",

    os.path.join(
        DISTANCE_SRC,
        "data_loader.py"
    )
)


distance_lookup = load_module(

    "distance_rule_lookup",

    os.path.join(
        DISTANCE_SRC,
        "distance_lookup.py"
    )
)


distance_calculation = load_module(

    "distance_calculation_module",

    os.path.join(
        DISTANCE_SRC,
        "distance_calculation.py"
    )
)


# =========================================================
# LOAD FUNCTIONS
# =========================================================

load_distance_rules = (
    distance_loader.load_distance_rules
)


get_maximum_distance = (
    distance_lookup.get_maximum_distance
)


calculate_nearest_provider_distances = (
    distance_calculation
    .calculate_nearest_provider_distances
)


calculate_distance_adequacy = (
    distance_calculation
    .calculate_distance_adequacy
)


# =========================================================
# CAPACITY INPUT
# =========================================================

def get_capacity():

    print(
        "\n"
        + "-" * 65
    )

    print(
        "CAPACITY CONFIGURATION"
    )

    print(
        "-" * 65
    )


    while True:

        user_input = input(
            "Enter capacity per provider: "
        ).strip()


        try:

            capacity = float(
                user_input
            )


            if capacity <= 0:

                print(
                    "❌ Capacity must be greater than zero."
                )

                continue


            return capacity


        except ValueError:

            print(
                "❌ Please enter a valid number."
            )


# =========================================================
# TOTAL ADEQUACY CALCULATION
# =========================================================

def calculate_total_adequacy(
    capacity_adequacy,
    distance_adequacy
):

    total_adequacy = (

        capacity_adequacy
        +
        distance_adequacy

    ) / 2


    return round(
        total_adequacy,
        2
    )


# =========================================================
# GET TOTAL STATUS
# =========================================================

def get_total_status(
    total_adequacy
):

    if total_adequacy >= 90:

        return "HIGHLY ADEQUATE"

    elif total_adequacy >= 75:

        return "ADEQUATE"

    elif total_adequacy >= 50:

        return "PARTIALLY ADEQUATE"

    else:

        return "INADEQUATE"


# =========================================================
# DISPLAY RESULT
# =========================================================

def display_result(
    state,
    city,
    specialty,
    capacity_adequacy,
    distance_adequacy,
    total_adequacy,
    status
):

    print(
        "\n"
        + "=" * 70
    )

    print(
        "                 TOTAL ADEQUACY RESULT"
    )

    print(
        "=" * 70
    )


    print(
        "\nLOCATION"
    )

    print(
        "-" * 70
    )

    print(
        f"State                    : {state}"
    )

    print(
        f"City/Town                : {city}"
    )

    print(
        f"Specialty                : {specialty}"
    )


    print(
        "\nADEQUACY COMPONENTS"
    )

    print(
        "-" * 70
    )

    print(
        f"Capacity Adequacy        : "
        f"{capacity_adequacy:.2f}%"
    )

    print(
        f"Distance Adequacy        : "
        f"{distance_adequacy:.2f}%"
    )


    print(
        "\nTOTAL ADEQUACY"
    )

    print(
        "-" * 70
    )

    print(
        "Formula:"
    )

    print(
        "Total Adequacy = "
        "(Capacity Adequacy + Distance Adequacy) / 2"
    )


    print(
        f"\nTotal Adequacy           : "
        f"{total_adequacy:.2f}%"
    )

    print(
        f"Overall Status           : "
        f"{status}"
    )


    print(
        "=" * 70
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "                  TOTAL NETWORK ADEQUACY"
    )

    print(
        "=" * 70
    )


    # =====================================================
    # LOAD DATA
    # =====================================================

    print(
        "\nLoading datasets..."
    )


    try:

        patients = (
            load_patient_data()
        )

        providers = (
            load_provider_data()
        )

        distance_rules = (
            load_distance_rules()
        )

    except Exception as error:

        print(
            "\n❌ DATA LOADING ERROR"
        )

        print(error)

        return


    # =====================================================
    # USER INPUT
    # =====================================================

    print(
        "\n"
        + "-" * 65
    )

    print(
        "NETWORK FILTER"
    )

    print(
        "-" * 65
    )


    state = input(
        "Enter State: "
    ).strip()


    city = input(
        "Enter City/Town: "
    ).strip()


    specialty = input(
        "Enter Specialty: "
    ).strip()


    # =====================================================
    # CAPACITY PER PROVIDER
    # =====================================================

    capacity_per_provider = (
        get_capacity()
    )


    # =====================================================
    # CAPACITY ADEQUACY
    # =====================================================

    print(
        "\n"
        + "-" * 65
    )

    print(
        "CALCULATING CAPACITY ADEQUACY..."
    )

    print(
        "-" * 65
    )


    try:

        filtered_patients = (
            filter_patients(

                patients,

                state,

                city,

                specialty
            )
        )


        filtered_providers = (
            filter_providers(

                providers,

                state,

                city,

                specialty
            )
        )


        patient_count = len(
            filtered_patients
        )


        provider_count = len(
            filtered_providers
        )


        capacity_result = (
            calculate_capacity_adequacy(

                provider_count,

                patient_count,

                capacity_per_provider
            )
        )


        capacity_adequacy = (
            capacity_result[
                "capacity_adequacy"
            ]
        )


        if capacity_adequacy is None:

            capacity_adequacy = 0


    except Exception as error:

        print(
            "\n❌ CAPACITY ADEQUACY ERROR"
        )

        print(error)

        return


    print(
        f"Patient Count            : "
        f"{patient_count}"
    )

    print(
        f"Provider Count           : "
        f"{provider_count}"
    )

    print(
        f"Capacity Adequacy        : "
        f"{capacity_adequacy:.2f}%"
    )


    # =====================================================
    # DISTANCE ADEQUACY
    # =====================================================

    print(
        "\n"
        + "-" * 65
    )

    print(
        "CALCULATING DISTANCE ADEQUACY..."
    )

    print(
        "-" * 65
    )


    try:

        # -------------------------------------------------
        # FIND MAXIMUM DISTANCE
        # -------------------------------------------------

        maximum_distance = (
            get_maximum_distance(

                distance_rules,

                state,

                city,

                specialty
            )
        )


        if maximum_distance is None:

            print(
                "\n❌ Maximum distance not found."
            )

            print(
                "Check State + City/Town + Specialty "
                "in capacity count.csv"
            )

            return


        print(
            f"Maximum Allowed Distance : "
            f"{maximum_distance} miles"
        )


        # -------------------------------------------------
        # FILTER PATIENTS
        # -------------------------------------------------

        patient_state = (
            patients["State"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        patient_city = (
            patients["City/Town"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        patient_specialty = (
            patients["Specialist"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        distance_patients = patients[

            (patient_state == state.upper())

            &

            (
                patient_city.str.contains(
                    city.upper(),
                    na=False,
                    regex=False
                )
            )

            &

            (
                patient_specialty.str.contains(
                    specialty.upper(),
                    na=False,
                    regex=False
                )
            )

        ].copy()


        # -------------------------------------------------
        # FILTER PROVIDERS
        # -------------------------------------------------

        provider_state = (
            providers["State"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        provider_city = (
            providers["City/Town"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        provider_specialty = (
            providers["pri_spec"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        distance_providers = providers[

            (provider_state == state.upper())

            &

            (
                provider_city.str.contains(
                    city.upper(),
                    na=False,
                    regex=False
                )
            )

            &

            (
                provider_specialty.str.contains(
                    specialty.upper(),
                    na=False,
                    regex=False
                )
            )

        ].copy()


        print(
            f"Patients for distance analysis : "
            f"{len(distance_patients)}"
        )


        print(
            f"Providers for distance analysis: "
            f"{len(distance_providers)}"
        )


        if distance_patients.empty:

            print(
                "\n❌ No patients found "
                "for distance analysis."
            )

            return


        if distance_providers.empty:

            print(
                "\n❌ No providers found "
                "for distance analysis."
            )

            return


        # -------------------------------------------------
        # HAVERSINE
        # -------------------------------------------------

        print(
            "\nCalculating Haversine distances..."
        )


        patient_distances = (
            calculate_nearest_provider_distances(

                distance_patients,

                distance_providers
            )
        )


        # -------------------------------------------------
        # DISTANCE ADEQUACY
        # -------------------------------------------------

        distance_result = (
            calculate_distance_adequacy(

                patient_distances,

                maximum_distance
            )
        )


        distance_adequacy = (
            distance_result[
                "distance_adequacy"
            ]
        )


    except Exception as error:

        print(
            "\n❌ DISTANCE ADEQUACY ERROR"
        )

        print(error)

        return


    print(
        f"Reasonable Patients      : "
        f"{distance_result['reasonable_patients']}"
    )


    print(
        f"Total Patients           : "
        f"{distance_result['total_patients']}"
    )


    print(
        f"Distance Adequacy        : "
        f"{distance_adequacy:.2f}%"
    )


    # =====================================================
    # TOTAL ADEQUACY
    # =====================================================

    print(
        "\n"
        + "-" * 65
    )

    print(
        "CALCULATING TOTAL ADEQUACY..."
    )

    print(
        "-" * 65
    )


    total_adequacy = (
        calculate_total_adequacy(

            capacity_adequacy,

            distance_adequacy
        )
    )


    status = get_total_status(
        total_adequacy
    )


    # =====================================================
    # FINAL RESULT
    # =====================================================

    display_result(

        state,

        city,

        specialty,

        capacity_adequacy,

        distance_adequacy,

        total_adequacy,

        status
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()
