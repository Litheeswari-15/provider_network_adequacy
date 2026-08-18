import pandas as pd
import os


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
# DISTANCE RULES FILE (capacity_count.csv)
# =========================================================

DISTANCE_RULES_FILE = os.path.join(
    DATASET_DIR,
    "capacity_count.csv"
)


# =========================================================
# NORMALIZE
# =========================================================

def normalize(value):

    return str(
        value
    ).strip().upper()


# =========================================================
# FIND COLUMN (Case-insensitive)
# =========================================================

def find_column(
    df,
    possible_names
):

    normalized_columns = {
        normalize(column): column
        for column in df.columns
    }

    for name in possible_names:

        normalized_name = normalize(name)

        if normalized_name in normalized_columns:

            return normalized_columns[
                normalized_name
            ]

    return None


# =========================================================
# LOAD DISTANCE RULES
# =========================================================

def load_distance_rules():

    print("Loading distance rules...")

    if not os.path.exists(DISTANCE_RULES_FILE):

        raise FileNotFoundError(
            f"Distance rules file not found:\n{DISTANCE_RULES_FILE}"
        )

    df = pd.read_csv(DISTANCE_RULES_FILE)

    print(
        f"Distance rules loaded: {len(df)} entries"
    )

    return df


# =========================================================
# GET MAXIMUM DISTANCE
# =========================================================

def get_maximum_distance(
    distance_rules,
    county,  # FIXED: Changed from 'state' to 'county'
    city,
    specialty
):

    """
    Get maximum allowed distance for a specific
    County/City/Specialty combination from capacity_count.csv
    """

    # FIXED: Changed "State" to "County"
    county_col = find_column(
        distance_rules,
        ["County"]
    )

    city_col = find_column(
        distance_rules,
        [
            "City/Town",
            "City",
            "Town"
        ]
    )

    specialty_col = find_column(
        distance_rules,
        [
            "Specialist",
            "Specialty",
            "pri_spec"
        ]
    )

    distance_col = find_column(
        distance_rules,
        [
            "Maximum_Distance_Miles",
            "Distance_Miles",
            "Max_Distance"
        ]
    )


    # Validation
    if county_col is None:

        raise KeyError(
            "County column not found in distance rules"
        )

    if city_col is None:

        raise KeyError(
            "City/Town column not found in distance rules"
        )

    if specialty_col is None:

        raise KeyError(
            "Specialty column not found in distance rules"
        )

    if distance_col is None:

        raise KeyError(
            "Distance column not found in distance rules"
        )


    # Normalize data
    distance_rules[county_col] = (
        distance_rules[county_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    distance_rules[city_col] = (
        distance_rules[city_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    distance_rules[specialty_col] = (
        distance_rules[specialty_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )


    # Filter for matching record
    filtered = distance_rules[
        (distance_rules[county_col] == normalize(county))
        & (distance_rules[city_col] == normalize(city))
        & (distance_rules[specialty_col] == normalize(specialty))
    ]


    if len(filtered) == 0:

        raise ValueError(
            f"No distance rule found for:\n"
            f"County: {county}\n"
            f"City: {city}\n"
            f"Specialty: {specialty}"
        )


    # Get the distance value
    maximum_distance = filtered[
        distance_col
    ].iloc[0]

    return float(maximum_distance)