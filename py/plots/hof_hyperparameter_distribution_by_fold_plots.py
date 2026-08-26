import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
from pandas import DataFrame

from util.hyperparameter_fold_distribution_plot_results import (
    save_hyperparameter_distribution_by_fold
)


HYPERPARAMETERS_DIR = "hyperparameters"

SOLUTION_HYPERPARAMETERS_PREFIX = (
    "solution_hyperparameters"
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

        solution_hyperparameters_fold_12.csv
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


def read_hyperparameters(
        file_path: str
) -> DataFrame:

    return pd.read_csv(
        file_path
    )


def hyperparameter_values_are_constant(
        hyperparameter_values
) -> bool:
    """
    Returns True when all non-missing values
    of a hyperparameter are identical.

    Constant hyperparameters are skipped.
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


def union_values_from_folds(
        hyperparameters_dfs_by_fold:
        dict[int, DataFrame],
        hyperparameter_name: str
):
    """
    Returns all values of one hyperparameter
    from every fold.
    """

    result = []

    for hyperparameters_df in (
            hyperparameters_dfs_by_fold.values()
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

        result.extend(
            hyperparameters_df[
                hyperparameter_name
            ].tolist()
        )

    return result


def hyperparameter_distribution_by_fold_plots_for_directory(
        hof_dir: str
):
    """
    Creates one distribution plot per
    non-constant hyperparameter.

    Every plot shows the distribution of the
    hyperparameter values across the folds.

    The final solutions are intentionally not
    included because the goal is to compare
    the distributions between folds.
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

    if len(
            hyperparameters_files_by_fold
    ) == 0:

        return

    hyperparameters_dfs_by_fold = {
        fold_number: read_hyperparameters(
            file_path=file_path
        )
        for (
                fold_number,
                file_path
        ) in (
            hyperparameters_files_by_fold.items()
        )
    }

    first_fold_number = min(
        hyperparameters_dfs_by_fold.keys()
    )

    first_hyperparameters_df = (
        hyperparameters_dfs_by_fold[
            first_fold_number
        ]
    )

    for hyperparameter_name in (
            first_hyperparameters_df.columns
    ):

        all_hyperparameter_values = (
            union_values_from_folds(
                hyperparameters_dfs_by_fold=(
                    hyperparameters_dfs_by_fold
                ),
                hyperparameter_name=(
                    hyperparameter_name
                )
            )
        )

        if (
            hyperparameter_values_are_constant(
                hyperparameter_values=(
                    all_hyperparameter_values
                )
            )
        ):

            continue

        values_by_fold = {}

        for (
                fold_number,
                hyperparameters_df
        ) in (
            hyperparameters_dfs_by_fold.items()
        ):

            if (
                hyperparameter_name
                not in hyperparameters_df.columns
            ):

                raise ValueError(
                    "Hyperparameter '"
                    + hyperparameter_name
                    + "' is not present "
                    "in fold "
                    + str(
                        fold_number
                    )
                    + "."
                )

            values_by_fold[
                fold_number
            ] = (
                hyperparameters_df[
                    hyperparameter_name
                ].tolist()
            )

        save_file = os.path.join(
            plot_dir,
            hyperparameter_name
            + "_distribution_by_fold.png"
        )

        save_hyperparameter_distribution_by_fold(
            values_by_fold=values_by_fold,
            save_file=save_file,
            hyperparameter_name=(
                hyperparameter_name
            )
        )


def hof_hyperparameter_distribution_by_fold_plots_every_hof(
        main_hofs_dir: str
):
    """
    Creates Hyperparameter distribution by fold
    plots for every Hall Of Fame directory.
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

        hyperparameter_distribution_by_fold_plots_for_directory(
            hof_dir=hof_dir
        )