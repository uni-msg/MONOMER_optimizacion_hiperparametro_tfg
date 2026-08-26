import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
from pandas import DataFrame

from util.hyperparameter_plot_results import (
    save_hyperparameter_multiclass_scatter
)


HYPERPARAMETERS_DIR = "hyperparameters"

SOLUTION_HYPERPARAMETERS_PREFIX = (
    "solution_hyperparameters"
)

SOLUTION_FEATURES_PREFIX = (
    "solution_features"
)

FOLD_FILE_REGEX = re.compile(
    r"_fold_(\d+)\.csv$"
)


def fold_number_from_file_name(
        file_name: str
) -> Optional[int]:
    """
    Returns the fold number from a file name.

    Examples:

        solution_hyperparameters_fold_0.csv
            -> 0

        solution_features_fold_12.csv
            -> 12

        solution_hyperparameters_final.csv
            -> None
    """

    match = FOLD_FILE_REGEX.search(
        file_name
    )

    if match is None:

        return None

    return int(
        match.group(1)
    )


def is_hyperparameters_file(
        file_name: str
) -> bool:

    return (
        file_name.startswith(
            SOLUTION_HYPERPARAMETERS_PREFIX
        )
        and file_name.endswith(
            ".csv"
        )
    )


def is_features_file(
        file_name: str
) -> bool:

    return (
        file_name.startswith(
            SOLUTION_FEATURES_PREFIX
        )
        and file_name.endswith(
            ".csv"
        )
    )


def hyperparameters_fold_files(
        hof_dir: str
) -> dict[int, str]:
    """
    Returns the hyperparameters files indexed
    by fold number.
    """

    result = {}

    if not os.path.isdir(
            hof_dir
    ):

        return result

    for file_name in os.listdir(
            hof_dir
    ):

        if not is_hyperparameters_file(
                file_name
        ):

            continue

        fold_number = (
            fold_number_from_file_name(
                file_name
            )
        )

        if fold_number is not None:

            result[
                fold_number
            ] = os.path.join(
                hof_dir,
                file_name
            )

    return result


def features_fold_files(
        hof_dir: str
) -> dict[int, str]:
    """
    Returns the features files indexed
    by fold number.
    """

    result = {}

    if not os.path.isdir(
            hof_dir
    ):

        return result

    for file_name in os.listdir(
            hof_dir
    ):

        if not is_features_file(
                file_name
        ):

            continue

        fold_number = (
            fold_number_from_file_name(
                file_name
            )
        )

        if fold_number is not None:

            result[
                fold_number
            ] = os.path.join(
                hof_dir,
                file_name
            )

    return result


def hyperparameters_final_file(
        hof_dir: str
) -> Optional[str]:
    """
    Returns the final hyperparameters file
    if it exists.
    """

    file_path = os.path.join(
        hof_dir,
        SOLUTION_HYPERPARAMETERS_PREFIX
        + "_final.csv"
    )

    if os.path.isfile(
            file_path
    ):

        return file_path

    return None


def features_final_file(
        hof_dir: str
) -> Optional[str]:
    """
    Returns the final features file.

    Supports both:

        solution_features_final.csv

    and:

        solution_features_fold_final.csv
    """

    possible_file_names = [
        (
            SOLUTION_FEATURES_PREFIX
            + "_final.csv"
        ),
        (
            SOLUTION_FEATURES_PREFIX
            + "_fold_final.csv"
        )
    ]

    for file_name in possible_file_names:

        file_path = os.path.join(
            hof_dir,
            file_name
        )

        if os.path.isfile(
                file_path
        ):

            return file_path

    return None


def read_hyperparameters(
        file_path: str
) -> DataFrame:

    return pd.read_csv(
        file_path
    )


def read_features(
        file_path: str
) -> DataFrame:

    return pd.read_csv(
        file_path
    )


def solution_complexities(
        features_df: DataFrame
) -> list[int]:
    """
    Computes the complexity of every solution.

    Complexity is defined as the number of
    selected features.

    A selected feature is represented by:

        1

    A non-selected feature is represented by:

        0

    Therefore, for every solution:

        complexity =
            number of selected features
    """

    numeric_features_df = (
        features_df.apply(
            pd.to_numeric,
            errors="coerce"
        )
    )

    return (
        numeric_features_df
        .eq(
            1
        )
        .sum(
            axis=1
        )
        .astype(
            int
        )
        .tolist()
    )


def hyperparameter_values_are_constant(
        hyperparameter_values
) -> bool:
    """
    Returns True when all non-missing values
    of a hyperparameter are identical.

    A constant hyperparameter does not provide
    useful information in a relationship plot.
    """

    series = pd.Series(
        hyperparameter_values
    )

    unique_values = (
        series
        .dropna()
        .drop_duplicates()
    )

    return len(
        unique_values
    ) <= 1


def plot_hyperparameter_vs_complexity(
        hyperparameter_values,
        complexities: list[int],
        save_file: str,
        hyperparameter_name: str
):
    """
    Creates a plot of:

        hyperparameter
            vs
        solution complexity

    Complexity is the number of selected
    features.

    The X axis is automatically selected by
    save_hyperparameter_multiclass_scatter:

        - categorical
        - integer
        - float
        - logarithmic when appropriate

    Constant hyperparameters are skipped.
    """

    if len(
            hyperparameter_values
    ) == 0:

        return

    if (
        hyperparameter_values_are_constant(
            hyperparameter_values=
            hyperparameter_values
        )
    ):

        return

    if (
        len(
            hyperparameter_values
        )
        != len(
            complexities
        )
    ):

        raise ValueError(
            "Different number of "
            "hyperparameter values and "
            "complexity values for "
            "hyperparameter "
            f"'{hyperparameter_name}'. "
            f"Hyperparameters: "
            f"{len(hyperparameter_values)}. "
            f"Complexities: "
            f"{len(complexities)}."
        )

    save_hyperparameter_multiclass_scatter(
        x=[
            hyperparameter_values
        ],
        y=[
            complexities
        ],
        save_file=save_file,
        x_label=hyperparameter_name,
        y_label=(
            "number of selected features"
        ),
        class_labels=[
            "solutions"
        ]
    )


def union_hyperparameters_vs_complexity_plots(
        hyperparameters_dfs: list[
            DataFrame
        ],
        features_dfs: list[
            DataFrame
        ],
        plot_dir: str
):
    """
    Creates one Hyperparameter vs complexity
    plot for every non-constant hyperparameter.

    All solutions from every fold are joined.

    The final solution is not included here.
    """

    if len(
            hyperparameters_dfs
    ) == 0:

        return

    if (
        len(hyperparameters_dfs)
        != len(features_dfs)
    ):

        raise ValueError(
            "Different number of "
            "hyperparameters and features "
            "dataframes."
        )

    first_hyperparameters_df = (
        hyperparameters_dfs[0]
    )

    for hyperparameter_name in (
            first_hyperparameters_df.columns
    ):

        union_hyperparameter_values = []
        union_complexities = []

        for (
                hyperparameters_df,
                features_df
        ) in zip(
            hyperparameters_dfs,
            features_dfs
        ):

            if (
                hyperparameter_name
                not in hyperparameters_df.columns
            ):

                raise ValueError(
                    "Hyperparameter '"
                    + hyperparameter_name
                    + "' is not present "
                    "in every fold."
                )

            hyperparameter_values = (
                hyperparameters_df[
                    hyperparameter_name
                ].tolist()
            )

            complexities = (
                solution_complexities(
                    features_df=features_df
                )
            )

            if (
                len(
                    hyperparameter_values
                )
                != len(
                    complexities
                )
            ):

                raise ValueError(
                    "Different number of "
                    "hyperparameter values and "
                    "feature solutions in one "
                    "fold for hyperparameter "
                    f"'{hyperparameter_name}'. "
                    f"Hyperparameters: "
                    f"{len(hyperparameter_values)}. "
                    f"Feature solutions: "
                    f"{len(complexities)}."
                )

            union_hyperparameter_values.extend(
                hyperparameter_values
            )

            union_complexities.extend(
                complexities
            )

        if (
            hyperparameter_values_are_constant(
                hyperparameter_values=(
                    union_hyperparameter_values
                )
            )
        ):

            continue

        save_file = os.path.join(
            plot_dir,
            hyperparameter_name
            + "_complexity.png"
        )

        plot_hyperparameter_vs_complexity(
            hyperparameter_values=(
                union_hyperparameter_values
            ),
            complexities=(
                union_complexities
            ),
            save_file=save_file,
            hyperparameter_name=(
                hyperparameter_name
            )
        )


def final_hyperparameters_vs_complexity_plots(
        hyperparameters_file: str,
        features_file: str,
        plot_dir: str
):
    """
    Creates one Hyperparameter vs complexity
    plot for every non-constant hyperparameter
    using the final solutions.
    """

    hyperparameters_df = (
        read_hyperparameters(
            file_path=hyperparameters_file
        )
    )

    features_df = (
        read_features(
            file_path=features_file
        )
    )

    complexities = (
        solution_complexities(
            features_df=features_df
        )
    )

    for hyperparameter_name in (
            hyperparameters_df.columns
    ):

        hyperparameter_values = (
            hyperparameters_df[
                hyperparameter_name
            ].tolist()
        )

        save_file = os.path.join(
            plot_dir,
            hyperparameter_name
            + "_complexity_final.png"
        )

        plot_hyperparameter_vs_complexity(
            hyperparameter_values=(
                hyperparameter_values
            ),
            complexities=(
                complexities
            ),
            save_file=save_file,
            hyperparameter_name=(
                hyperparameter_name
            )
        )


def hof_hyperparameter_complexity_plots_for_directory(
        hof_dir: str
):
    """
    Creates Hyperparameter vs complexity plots
    for one Hall Of Fame directory.

    Expected files:

        solution_hyperparameters_fold_0.csv
        solution_features_fold_0.csv

        solution_hyperparameters_fold_1.csv
        solution_features_fold_1.csv

        ...

    Final files:

        solution_hyperparameters_final.csv

    and one of:

        solution_features_final.csv
        solution_features_fold_final.csv

    Complexity is calculated as the number of
    selected features.

    Output:

        hof_dir/hyperparameters/
    """

    if not os.path.isdir(
            hof_dir
    ):

        return

    plot_dir = os.path.join(
        hof_dir,
        HYPERPARAMETERS_DIR
    )

    Path(
        plot_dir
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    hyperparameters_files_by_fold = (
        hyperparameters_fold_files(
            hof_dir=hof_dir
        )
    )

    features_files_by_fold = (
        features_fold_files(
            hof_dir=hof_dir
        )
    )

    common_folds = sorted(
        set(
            hyperparameters_files_by_fold.keys()
        )
        & set(
            features_files_by_fold.keys()
        )
    )

    hyperparameters_dfs = []
    features_dfs = []

    for fold_number in common_folds:

        hyperparameters_file = (
            hyperparameters_files_by_fold[
                fold_number
            ]
        )

        features_file = (
            features_files_by_fold[
                fold_number
            ]
        )

        hyperparameters_dfs.append(
            read_hyperparameters(
                file_path=hyperparameters_file
            )
        )

        features_dfs.append(
            read_features(
                file_path=features_file
            )
        )

    union_hyperparameters_vs_complexity_plots(
        hyperparameters_dfs=(
            hyperparameters_dfs
        ),
        features_dfs=features_dfs,
        plot_dir=plot_dir
    )

    final_hyperparameters_file = (
        hyperparameters_final_file(
            hof_dir=hof_dir
        )
    )

    final_features_file = (
        features_final_file(
            hof_dir=hof_dir
        )
    )

    if (
        final_hyperparameters_file
        is not None
        and final_features_file
        is not None
    ):

        final_hyperparameters_vs_complexity_plots(
            hyperparameters_file=(
                final_hyperparameters_file
            ),
            features_file=(
                final_features_file
            ),
            plot_dir=plot_dir
        )


def hof_hyperparameter_complexity_plots_every_hof(
        main_hofs_dir: str
):
    """
    Creates Hyperparameter vs complexity plots
    for every Hall Of Fame directory.
    """

    if not os.path.isdir(
            main_hofs_dir
    ):

        return

    subfolders = [
        folder.path
        for folder in os.scandir(
            main_hofs_dir
        )
        if folder.is_dir()
    ]

    for hof_dir in subfolders:

        hof_hyperparameter_complexity_plots_for_directory(
            hof_dir=hof_dir
        )