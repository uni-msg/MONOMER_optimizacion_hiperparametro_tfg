import math
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


LOG_SCALE_MIN_RATIO = 100


def flatten_values(
        values_by_class
) -> list:
    """
    Flattens all values from every class.
    """

    result = []

    for values in values_by_class:

        result.extend(
            values
        )

    return result


def is_missing_value(
        value
) -> bool:
    """
    Returns True if the value represents
    a missing value.
    """

    try:

        return bool(
            pd.isna(value)
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
    whether the hyperparameter is numeric.

    Returns None when at least one non-missing
    value cannot be converted to a number.
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
        and len(numeric_values) > 0
    )


def hyperparameter_is_integer(
        values
) -> bool:
    """
    Returns True when all non-missing values
    are integer values.

    Examples:

        10
        25
        100

    are integers.

        0.1
        1e-8

    are not.
    """

    numeric_values = (
        numeric_values_or_none(
            values=values
        )
    )

    if (
        numeric_values is None
        or len(numeric_values) == 0
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
    Determines whether a numeric hyperparameter
    should use a logarithmic X axis.

    Rules:

        - categorical values -> no log scale
        - integer hyperparameters -> linear scale
        - zero or negative values -> linear scale
        - positive float values spanning at least
          two orders of magnitude -> log scale

    Examples:

        1e-12 ... 1e-8
            -> logarithmic

        0.1 ... 0.5
            -> linear

        10 ... 100
            -> linear

        1 ... 1000
            -> linear if integer values
    """

    numeric_values = (
        numeric_values_or_none(
            values=values
        )
    )

    if (
        numeric_values is None
        or len(numeric_values) < 2
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

    ratio = (
        maximum_value
        / minimum_value
    )

    return (
        ratio
        >= LOG_SCALE_MIN_RATIO
    )


def categorical_value(
        value
) -> str:
    """
    Converts one value into a categorical label.

    Missing values are represented as
    '<missing>'.
    """

    if is_missing_value(
            value
    ):

        return "None"

    return str(
        value
    )


def hyperparameter_has_multiple_values(
        values
) -> bool:
    """
    Returns True when a hyperparameter has
    more than one different value.

    Missing values are also considered a value
    because they can represent a valid
    hyperparameter option, such as None.
    """

    unique_values = set()

    for value in values:

        unique_values.add(
            categorical_value(
                value=value
            )
        )

    return (
        len(
            unique_values
        )
        > 1
    )


def categorical_information(
        values
) -> tuple:
    """
    Creates categorical labels and their
    corresponding X positions.

    Category order is determined by the
    order in which values first appear.
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


def numeric_x_and_y(
        x_values,
        y_values
) -> tuple:
    """
    Removes rows with missing or invalid
    numeric X or Y values.
    """

    filtered_x = []
    filtered_y = []

    for (
            x_value,
            y_value
    ) in zip(
        x_values,
        y_values
    ):

        if (
            is_missing_value(
                x_value
            )
            or is_missing_value(
                y_value
            )
        ):

            continue

        try:

            numeric_x = float(
                x_value
            )

            numeric_y = float(
                y_value
            )

        except (
                TypeError,
                ValueError
        ):

            continue

        if (
            not math.isfinite(
                numeric_x
            )
            or not math.isfinite(
                numeric_y
            )
        ):

            continue

        filtered_x.append(
            numeric_x
        )

        filtered_y.append(
            numeric_y
        )

    return (
        filtered_x,
        filtered_y
    )


def categorical_x_and_y(
        x_values,
        y_values,
        category_positions
) -> tuple:
    """
    Converts categorical values into X positions.

    Rows with missing Y values are ignored.
    Missing X values are represented by the
    '<missing>' category.
    """

    filtered_x = []
    filtered_y = []

    for (
            x_value,
            y_value
    ) in zip(
        x_values,
        y_values
    ):

        if is_missing_value(
                y_value
        ):

            continue

        try:

            numeric_y = float(
                y_value
            )

        except (
                TypeError,
                ValueError
        ):

            continue

        if not math.isfinite(
                numeric_y
        ):

            continue

        label = categorical_value(
            value=x_value
        )

        filtered_x.append(
            category_positions[
                label
            ]
        )

        filtered_y.append(
            numeric_y
        )

    return (
        filtered_x,
        filtered_y
    )


def validate_values_by_class(
        x,
        y,
        class_labels
):
    """
    Validates the dimensions of the input.
    """

    if (
        len(x)
        != len(y)
    ):

        raise ValueError(
            "Different number of X and Y "
            "datasets."
        )

    if (
        len(x)
        != len(class_labels)
    ):

        raise ValueError(
            "Different number of datasets "
            "and class labels."
        )

    for (
            x_values,
            y_values,
            class_label
    ) in zip(
        x,
        y,
        class_labels
    ):

        if (
            len(x_values)
            != len(y_values)
        ):

            raise ValueError(
                "Different number of X and Y "
                "values for class "
                f"'{class_label}'. "
                f"X: {len(x_values)}. "
                f"Y: {len(y_values)}."
            )


def save_hyperparameter_multiclass_scatter(
        x,
        y,
        save_file: str,
        x_label: str,
        y_label: str,
        class_labels
):
    """
    Creates and saves a scatter plot for a
    hyperparameter.

    The X axis is selected automatically:

        1. Categorical values:
           categorical axis.

        2. Integer values:
           linear numeric axis.

        3. Normal float values:
           linear numeric axis.

        4. Positive float values spanning
           multiple orders of magnitude:
           logarithmic numeric axis.
    """

    validate_values_by_class(
        x=x,
        y=y,
        class_labels=class_labels
    )

    all_x_values = flatten_values(
        values_by_class=x
    )

    if not hyperparameter_has_multiple_values(
            values=all_x_values
    ):
        return

    numeric = (
        hyperparameter_is_numeric(
            values=all_x_values
        )
    )

    figure, axis = plt.subplots()

    plotted_class_labels = []

    if numeric:

        use_log_scale = (
            hyperparameter_should_use_log_scale(
                values=all_x_values
            )
        )

        for (
                x_values,
                y_values,
                class_label
        ) in zip(
            x,
            y,
            class_labels
        ):

            (
                numeric_x,
                numeric_y
            ) = (
                numeric_x_and_y(
                    x_values=x_values,
                    y_values=y_values
                )
            )

            if len(
                    numeric_x
            ) == 0:

                continue

            axis.scatter(
                numeric_x,
                numeric_y,
                label=class_label
            )

            plotted_class_labels.append(
                class_label
            )

        if use_log_scale:

            axis.set_xscale(
                "log"
            )

    else:

        (
            category_labels,
            category_positions
        ) = (
            categorical_information(
                values=all_x_values
            )
        )

        for (
                x_values,
                y_values,
                class_label
        ) in zip(
            x,
            y,
            class_labels
        ):

            (
                categorical_x,
                numeric_y
            ) = (
                categorical_x_and_y(
                    x_values=x_values,
                    y_values=y_values,
                    category_positions=(
                        category_positions
                    )
                )
            )

            if len(
                    categorical_x
            ) == 0:

                continue

            axis.scatter(
                categorical_x,
                numeric_y,
                label=class_label
            )

            plotted_class_labels.append(
                class_label
            )

        axis.set_xticks(
            list(
                range(
                    len(
                        category_labels
                    )
                )
            )
        )

        axis.set_xticklabels(
            category_labels,
            rotation=45,
            ha="right"
        )

    axis.set_xlabel(
        x_label
    )

    axis.set_ylabel(
        y_label
    )

    axis.grid(
        True
    )

    if len(
            plotted_class_labels
    ) > 0:

        axis.legend()

    figure.tight_layout()

    figure.savefig(
        save_file
    )

    plt.close(
        figure
    )