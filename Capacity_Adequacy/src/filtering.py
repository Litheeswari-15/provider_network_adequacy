def normalize(value):

    return str(
        value
    ).strip().upper()


# =========================================================
# FIND COLUMN
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

        normalized_name = normalize(
            name
        )

        if normalized_name in normalized_columns:

            return normalized_columns[
                normalized_name
            ]

    return None


# =========================================================
# FILTER PATIENTS
# =========================================================

def filter_patients(
    df,
    state,
    city,
    specialty
):

    result = df.copy()


    state_col = find_column(
        result,
        ["State"]
    )

    city_col = find_column(
        result,
        [
            "City/Town",
            "City",
            "Town"
        ]
    )

    specialty_col = find_column(
        result,
        [
            "Specialist",
            "Specialty"
        ]
    )


    if state_col is None:

        raise KeyError(
            "State column not found "
            "in patient dataset."
        )


    if city_col is None:

        raise KeyError(
            "City/Town column not found "
            "in patient dataset."
        )


    if specialty_col is None:

        raise KeyError(
            "Specialist column not found "
            "in patient dataset."
        )


    # -----------------------------------------------------
    # NORMALIZE DATA
    # -----------------------------------------------------

    result[state_col] = (
        result[state_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    result[city_col] = (
        result[city_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    result[specialty_col] = (
        result[specialty_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )


    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    result = result[
        result[state_col]
        == normalize(state)
    ]


    result = result[
        result[city_col]
        .str.contains(
            normalize(city),
            na=False,
            regex=False
        )
    ]


    result = result[
        result[specialty_col]
        .str.contains(
            normalize(specialty),
            na=False,
            regex=False
        )
    ]


    return result


# =========================================================
# FILTER PROVIDERS
# =========================================================

def filter_providers(
    df,
    state,
    city,
    specialty
):

    result = df.copy()


    state_col = find_column(
        result,
        ["State"]
    )

    city_col = find_column(
        result,
        [
            "City/Town",
            "City",
            "Town"
        ]
    )

    specialty_col = find_column(
        result,
        [
            "pri_spec",
            "Specialist",
            "Specialty"
        ]
    )


    if state_col is None:

        raise KeyError(
            "State column not found "
            "in provider dataset."
        )


    if city_col is None:

        raise KeyError(
            "City/Town column not found "
            "in provider dataset."
        )


    if specialty_col is None:

        raise KeyError(
            "pri_spec column not found "
            "in provider dataset."
        )


    # -----------------------------------------------------
    # NORMALIZE DATA
    # -----------------------------------------------------

    result[state_col] = (
        result[state_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    result[city_col] = (
        result[city_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    result[specialty_col] = (
        result[specialty_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )


    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    result = result[
        result[state_col]
        == normalize(state)
    ]


    result = result[
        result[city_col]
        .str.contains(
            normalize(city),
            na=False,
            regex=False
        )
    ]


    result = result[
        result[specialty_col]
        .str.contains(
            normalize(specialty),
            na=False,
            regex=False
        )
    ]


    return result