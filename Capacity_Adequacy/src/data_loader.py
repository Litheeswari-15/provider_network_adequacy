import os
import pandas as pd


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..")
)

DATASET_DIR = os.path.join(
    PROJECT_DIR,
    "dataset"
)


# =========================================================
# DATASET PATHS
# =========================================================

PATIENT_FILE = os.path.join(
    DATASET_DIR,
    "patient_dataset.xlsx"
)

PROVIDER_FILE = os.path.join(
    DATASET_DIR,
    "provider_dataset.xlsx"
)


# =========================================================
# LOAD PATIENT DATA
# =========================================================

def load_patient_data():

    print("Loading patient dataset...")

    if not os.path.exists(PATIENT_FILE):

        raise FileNotFoundError(
            f"Patient dataset not found:\n{PATIENT_FILE}"
        )

    df = pd.read_excel(
        PATIENT_FILE
    )

    print(
        f"Patients loaded: {len(df)}"
    )

    return df


# =========================================================
# LOAD PROVIDER DATA
# =========================================================

def load_provider_data():

    print("Loading provider dataset...")

    if not os.path.exists(PROVIDER_FILE):

        raise FileNotFoundError(
            f"Provider dataset not found:\n{PROVIDER_FILE}"
        )

    df = pd.read_excel(
        PROVIDER_FILE
    )

    print(
        f"Providers loaded: {len(df)}"
    )

    return df