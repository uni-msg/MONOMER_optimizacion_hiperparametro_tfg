import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


LOG_SCALE_MIN_RATIO = 100


def is_missing_value(
        value
) -> bool:
    """
    Returns True when the value represents
    a missing value.
    """

    try:

        return bool(
            pd.isna(
                value
            )
        )

    except (
            TypeError,
            ValueError
    ):

        return False


def numeric_values_or_none(
        values
) -> Optional[list[float]]:
    """
    Converts values to numeric values.

    Missing values are ignored when deciding
    whether the values are numeric.

    Returns None when at least one non-missing
    value cannot be converted to a finite number.
    """

    numeric_values = []

    for value in values:

        if is_missing_value(
                value
        ):

            continue

        try:

            numeric_value = float(
                value
            )

        except (
                TypeError,
                ValueError
        ):

            return None

        if not math.isfinite(
                numeric_value
        ):

            return None

        numeric_values.append(
            numeric_value
        )

    return numeric_values


def hyperparameter_is_numeric(
        values
) -> bool:
    """
    Returns True when all non-missing values
    are numeric.
    """

    numeric_values = (
        numeric_values_or_none(
            values=values
        )
    )

    return (
        numeric_values is not None
        and len(
            numeric_values
        ) > 0
    )


def hyperparameter_is_integer(
        values
) -> bool:
    """
    Returns True when every non-missing value
    is an integer.
    """

    numeric_values = (
        numeric_values_or_none(
            values=values
        )
    )

    if (
        numeric_values is None
        or len(
            numeric_values
        ) == 0
    ):

        return False

    return all(
        value.is_integer()
        for value in numeric_values
    )


def hyperparameter_should_use_log_scale(
        values
) -> bool:
    """
    Determines whether a hyperparameter
    should use a logarithmic scale.

    Rules:

        - categorical -> no log scale
        - integer -> linear
        - zero/negative -> linear
        - positive floats with a range spanning
          at least two orders of magnitude
          -> logarithmic
    """

    numeric_values = (
        numeric_values_or_none(
            values=values
        )
    )

    if (
        numeric_values is None
        or len(
            numeric_values
        ) < 2
    ):

        return False

    if hyperparameter_is_integer(
            values=values
    ):

        return False

    unique_values = sorted(
        set(
            numeric_values
        )
    )

    if len(
            unique_values
    ) < 2:

        return False

    minimum_value = min(
        unique_values
    )

    maximum_value = max(
        unique_values
    )

    if minimum_value <= 0:

        return False

    return (
        maximum_value
        / minimum_value
        >= LOG_SCALE_MIN_RATIO
    )


def categorical_value(
        value
) -> str:
    """
    Converts a value into a categorical label.

    Missing values are represented as:

        <missing>
    """

    if is_missing_value(
            value
    ):

        return "<missing>"

    return str(
        value
    )


def categorical_information(
        values
) -> tuple[
    list[str],
    dict[str, int]
]:
    """
    Creates category labels and positions.
    """

    labels = []

    for value in values:

        label = categorical_value(
            value=value
        )

        if label not in labels:

            labels.append(
                label
            )

    positions = {
        label: position
        for (
                position,
                label
        ) in enumerate(
            labels
        )
    }

    return (
        labels,
        positions
    )


def numeric_values_by_fold(
        values_by_fold: dict[
            int,
            list
        ]
) -> dict[
    int,
    list[float]
]:
    """
    Converts numeric fold values to finite
    numeric values.
    """

    result = {}

    for (
            fold_number,
            values
    ) in (
        values_by_fold.items()
    ):

        numeric_values = []

        for value in values:

            if is_missing_value(
                    value
            ):

                continue

            try:

                numeric_value = float(
                    value
                )

            except (
                    TypeError,
                    ValueError
            ):

                continue

            if math.isfinite(
                    numeric_value
            ):

                numeric_values.append(
                    numeric_value
                )

        result[
            fold_number
        ] = numeric_values

    return result


def categorical_values_by_fold(
        values_by_fold: dict[
            int,
            list
        ],
        category_positions: dict[
            str,
            int
        ]
) -> dict[
    int,
    list[int]
]:
    """
    Converts categorical values to their
    category positions.
    """

    result = {}

    for (
            fold_number,
            values
    ) in (
        values_by_fold.items()
    ):

        result[
            fold_number
        ] = [
            category_positions[
                categorical_value(
                    value=value
                )
            ]
            for value in values
        ]

    return result


def jittered_positions(
        position: int,
        number_of_values: int
) -> np.ndarray:
    """
    Creates slightly jittered X positions so
    overlapping points remain visible.
    """

    if number_of_values == 0:

        return np.array(
            []
        )

    return (
        np.full(
            number_of_values,
            position,
            dtype=float
        )
        + np.random.uniform(
            -0.18,
            0.18,
            size=number_of_values
        )
    )


def save_hyperparameter_distribution_by_fold(
        values_by_fold: dict[
            int,
            list
        ],
        save_file: str,
        hyperparameter_name: str
):
    """
    Creates a distribution plot of one
    hyperparameter across the folds.

    X axis:

        Fold number

    Y axis:

        Hyperparameter value

    Numeric hyperparameters:

        - integer -> linear axis
        - float -> linear axis
        - wide positive float range
          -> logarithmic axis

    Categorical hyperparameters:

        categorical Y axis.

    Every solution is represented by one
    slightly jittered point.
    """

    if len(
            values_by_fold
    ) == 0:

        return

    sorted_folds = sorted(
        values_by_fold.keys()
    )

    all_values = []

    for values in (
            values_by_fold.values()
    ):

        all_values.extend(
            values
        )

    numeric = (
        hyperparameter_is_numeric(
            values=all_values
        )
    )

    figure, axis = plt.subplots()

    fold_positions = {
        fold_number: position
        for (
                position,
                fold_number
        ) in enumerate(
            sorted_folds
        )
    }

    if numeric:

        use_log_scale = (
            hyperparameter_should_use_log_scale(
                values=all_values
            )
        )

        numeric_by_fold = (
            numeric_values_by_fold(
                values_by_fold=(
                    values_by_fold
                )
            )
        )

        for fold_number in sorted_folds:

            values = (
                numeric_by_fold[
                    fold_number
                ]
            )

            if len(
                    values
            ) == 0:

                continue

            x_positions = (
                jittered_positions(
                    position=(
                        fold_positions[
                            fold_number
                        ]
                    ),
                    number_of_values=(
                        len(
                            values
                        )
                    )
                )
            )

            axis.scatter(
                x_positions,
                values
            )

        if use_log_scale:

            axis.set_yscale(
                "log"
            )

    else:

        (
            category_labels,
            category_positions
        ) = (
            categorical_information(
                values=all_values
            )
        )

        categorical_by_fold = (
            categorical_values_by_fold(
                values_by_fold=(
                    values_by_fold
                ),
                category_positions=(
                    category_positions
                )
            )
        )

        for fold_number in sorted_folds:

            values = (
                categorical_by_fold[
                    fold_number
                ]
            )

            if len(
                    values
            ) == 0:

                continue

            x_positions = (
                jittered_positions(
                    position=(
                        fold_positions[
                            fold_number
                        ]
                    ),
                    number_of_values=(
                        len(
                            values
                        )
                    )
                )
            )

            axis.scatter(
                x_positions,
                values
            )

        axis.set_yticks(
            list(
                range(
                    len(
                        category_labels
                    )
                )
            )
        )

        axis.set_yticklabels(
            category_labels
        )

    axis.set_xticks(
        list(
            fold_positions.values()
        )
    )

    axis.set_xticklabels(
        [
            "fold "
            + str(
                fold_number
            )
            for fold_number in sorted_folds
        ]
    )

    axis.set_xlabel(
        "fold"
    )

    axis.set_ylabel(
        hyperparameter_name
    )

    axis.set_title(
        hyperparameter_name
        + " distribution by fold"
    )

    axis.grid(
        True,
        axis="y"
    )

    figure.tight_layout()

    figure.savefig(
        save_file
    )

    plt.close(
        figure
    )