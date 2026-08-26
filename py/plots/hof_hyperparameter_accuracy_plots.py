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

SOLUTION_FITNESSES_PREFIX = (
    "solution_fitnesses"
)

FOLD_FILE_REGEX = re.compile(
    r"_fold_(\d+)\.csv$"
)

INNER_CV_PREFIX = "inner_cv__"
TRAIN_PREFIX = "train_"
TEST_PREFIX = "test_"

BALANCED_ACCURACY_SUFFIX = "_bal_acc"


def fold_number_from_file_name(
        file_name: str
) -> Optional[int]:
    """
    Returns the fold number from a file name.

    Examples:
        solution_hyperparameters_fold_0.csv -> 0
        solution_fitnesses_fold_12.csv -> 12
        solution_hyperparameters_final.csv -> None
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


def is_fitnesses_file(
        file_name: str
) -> bool:

    return (
        file_name.startswith(
            SOLUTION_FITNESSES_PREFIX
        )
        and file_name.endswith(
            ".csv"
        )
    )


def is_final_file(
        file_name: str
) -> bool:

    return file_name.endswith(
        "_final.csv"
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


def fitnesses_fold_files(
        hof_dir: str
) -> dict[int, str]:
    """
    Returns the fitnesses files indexed
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

        if not is_fitnesses_file(
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


def fitnesses_final_file(
        hof_dir: str
) -> Optional[str]:
    """
    Returns the final fitnesses file
    if it exists.
    """

    file_path = os.path.join(
        hof_dir,
        SOLUTION_FITNESSES_PREFIX
        + "_final.csv"
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


def read_fitnesses(
        file_path: str
) -> DataFrame:

    return pd.read_csv(
        file_path
    )


def inner_cv_balanced_accuracy_column(
        df: DataFrame
) -> Optional[str]:
    """
    Finds the balanced accuracy column
    corresponding to inner CV.
    """

    for column in df.columns:

        if (
            column.startswith(
                INNER_CV_PREFIX
            )
            and column.endswith(
                BALANCED_ACCURACY_SUFFIX
            )
        ):

            return column

    return None


def train_balanced_accuracy_column(
        df: DataFrame
) -> Optional[str]:
    """
    Finds the balanced accuracy column
    corresponding to train.
    """

    for column in df.columns:

        if (
            column.startswith(
                TRAIN_PREFIX
            )
            and column.endswith(
                BALANCED_ACCURACY_SUFFIX
            )
        ):

            return column

    return None


def test_balanced_accuracy_column(
        df: DataFrame
) -> Optional[str]:
    """
    Finds the balanced accuracy column
    corresponding to test.
    """

    for column in df.columns:

        if (
            column.startswith(
                TEST_PREFIX
            )
            and column.endswith(
                BALANCED_ACCURACY_SUFFIX
            )
        ):

            return column

    return None


def balanced_accuracy_values_by_set(
        fitnesses_df: DataFrame
) -> dict[str, list[float]]:
    """
    Extracts balanced accuracy values for:

        - train
        - inner cv
        - test
    """

    result = {}

    inner_cv_column = (
        inner_cv_balanced_accuracy_column(
            df=fitnesses_df
        )
    )

    train_column = (
        train_balanced_accuracy_column(
            df=fitnesses_df
        )
    )

    test_column = (
        test_balanced_accuracy_column(
            df=fitnesses_df
        )
    )

    if train_column is not None:

        result["train"] = (
            fitnesses_df[
                train_column
            ].tolist()
        )

    if inner_cv_column is not None:

        result["inner cv"] = (
            fitnesses_df[
                inner_cv_column
            ].tolist()
        )

    if test_column is not None:

        result["test"] = (
            fitnesses_df[
                test_column
            ].tolist()
        )

    return result


def plot_hyperparameter_vs_balanced_accuracy(
        hyperparameter_values,
        balanced_accuracies_by_set: dict[
            str,
            list[float]
        ],
        save_file: str,
        hyperparameter_name: str
):
    """
    Creates one scatter plot.

    X:
        Values of one hyperparameter.

    Y:
        Balanced accuracy.

    Different colours:

        - train
        - inner cv
        - test

    The hyperparameter type is detected
    automatically by the plotting function.

    Supported automatically:

        - integer values
        - float values
        - logarithmic float values
        - categorical values
        - boolean values
        - missing values
        - mixed values
    """

    if len(
            hyperparameter_values
    ) == 0:

        return

    x = []
    y = []

    class_labels = []

    for (
            set_name,
            balanced_accuracies
    ) in (
        balanced_accuracies_by_set.items()
    ):

        if len(
                balanced_accuracies
        ) == 0:

            continue

        if (
            len(
                hyperparameter_values
            )
            != len(
                balanced_accuracies
            )
        ):

            raise ValueError(
                "Different number of "
                "hyperparameter values and "
                "balanced accuracy values for "
                "hyperparameter "
                f"'{hyperparameter_name}'. "
                f"Hyperparameters: "
                f"{len(hyperparameter_values)}. "
                f"Balanced accuracies "
                f"({set_name}): "
                f"{len(balanced_accuracies)}."
            )

        x.append(
            hyperparameter_values
        )

        y.append(
            balanced_accuracies
        )

        class_labels.append(
            set_name
        )

    if len(
            x
    ) == 0:

        return

    save_hyperparameter_multiclass_scatter(
        x=x,
        y=y,
        save_file=save_file,
        x_label=hyperparameter_name,
        y_label="balanced accuracy",
        class_labels=class_labels
    )


def fold_hyperparameters_vs_balanced_accuracy_plots(
        hyperparameters_file: str,
        fitnesses_file: str,
        plot_dir: str,
        fold_number: int
):
    """
    Creates one plot for every numeric
    hyperparameter for one fold.
    """

    hyperparameters_df = (
        read_hyperparameters(
            file_path=hyperparameters_file
        )
    )

    fitnesses_df = (
        read_fitnesses(
            file_path=fitnesses_file
        )
    )

    balanced_accuracies_by_set = (
        balanced_accuracy_values_by_set(
            fitnesses_df=fitnesses_df
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
            + "_balanced_accuracy_fold_"
            + str(fold_number)
            + ".png"
        )

        plot_hyperparameter_vs_balanced_accuracy(
            hyperparameter_values=(
                hyperparameter_values
            ),
            balanced_accuracies_by_set=(
                balanced_accuracies_by_set
            ),
            save_file=save_file,
            hyperparameter_name=(
                hyperparameter_name
            )
        )


def union_hyperparameters_vs_balanced_accuracy_plots(
        hyperparameters_dfs: list[
            DataFrame
        ],
        fitnesses_dfs: list[
            DataFrame
        ],
        plot_dir: str
):
    """
    Creates one plot for every numeric
    hyperparameter using the union of all
    solutions from all folds.

    The final solution is not included here.
    """

    if len(
            hyperparameters_dfs
    ) == 0:

        return

    if (
        len(hyperparameters_dfs)
        != len(fitnesses_dfs)
    ):

        raise ValueError(
            "Different number of "
            "hyperparameter and fitnesses "
            "dataframes."
        )

    first_hyperparameters_df = (
        hyperparameters_dfs[0]
    )

    for hyperparameter_name in (
            first_hyperparameters_df.columns
    ):

        union_hyperparameter_values = []

        union_balanced_accuracies_by_set = {
            "train": [],
            "inner cv": [],
            "test": []
        }

        for (
                hyperparameters_df,
                fitnesses_df
        ) in zip(
            hyperparameters_dfs,
            fitnesses_dfs
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

            balanced_accuracies_by_set = (
                balanced_accuracy_values_by_set(
                    fitnesses_df=fitnesses_df
                )
            )

            union_hyperparameter_values.extend(
                hyperparameter_values
            )

            for (
                    set_name,
                    balanced_accuracies
            ) in (
                balanced_accuracies_by_set.items()
            ):

                if (
                    set_name
                    not in (
                        union_balanced_accuracies_by_set
                    )
                ):

                    union_balanced_accuracies_by_set[
                        set_name
                    ] = []

                union_balanced_accuracies_by_set[
                    set_name
                ].extend(
                    balanced_accuracies
                )

        union_balanced_accuracies_by_set = {
            set_name: values
            for (
                set_name,
                values
            ) in (
                union_balanced_accuracies_by_set.items()
            )
            if len(values) > 0
        }

        save_file = os.path.join(
            plot_dir,
            hyperparameter_name
            + "_balanced_accuracy.png"
        )

        plot_hyperparameter_vs_balanced_accuracy(
            hyperparameter_values=(
                union_hyperparameter_values
            ),
            balanced_accuracies_by_set=(
                union_balanced_accuracies_by_set
            ),
            save_file=save_file,
            hyperparameter_name=(
                hyperparameter_name
            )
        )


def final_hyperparameters_vs_balanced_accuracy_plots(
        hyperparameters_file: str,
        fitnesses_file: str,
        plot_dir: str
):
    """
    Creates one plot for every numeric
    hyperparameter using the final solutions.

    The final evaluation normally has:

        - inner cv
        - train

    but no test values.
    """

    hyperparameters_df = (
        read_hyperparameters(
            file_path=hyperparameters_file
        )
    )

    fitnesses_df = (
        read_fitnesses(
            file_path=fitnesses_file
        )
    )

    balanced_accuracies_by_set = (
        balanced_accuracy_values_by_set(
            fitnesses_df=fitnesses_df
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
            + "_balanced_accuracy_final.png"
        )

        plot_hyperparameter_vs_balanced_accuracy(
            hyperparameter_values=(
                hyperparameter_values
            ),
            balanced_accuracies_by_set=(
                balanced_accuracies_by_set
            ),
            save_file=save_file,
            hyperparameter_name=(
                hyperparameter_name
            )
        )


def hof_hyperparameter_accuracy_plots_for_directory(
        hof_dir: str
):
    """
    Creates hyperparameter vs balanced accuracy
    plots for one HOF.

    Expected input files:

        solution_hyperparameters_fold_0.csv
        solution_fitnesses_fold_0.csv

        solution_hyperparameters_fold_1.csv
        solution_fitnesses_fold_1.csv

        ...

        solution_hyperparameters_final.csv
        solution_fitnesses_final.csv

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

    fitnesses_files_by_fold = (
        fitnesses_fold_files(
            hof_dir=hof_dir
        )
    )

    common_folds = sorted(
        set(
            hyperparameters_files_by_fold.keys()
        )
        & set(
            fitnesses_files_by_fold.keys()
        )
    )

    hyperparameters_dfs = []
    fitnesses_dfs = []

    for fold_number in common_folds:
        hyperparameters_file = (hyperparameters_files_by_fold[fold_number])
        fitnesses_file = (fitnesses_files_by_fold[fold_number])

        # Se puede quitar la funcion comentada si buscamos obtener las graficas de HP vs accuracy x fold
        # fold_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_file=( hyperparameters_file),fitnesses_file=fitnesses_file,plot_dir=plot_dir,fold_number=fold_number)

        hyperparameters_dfs.append( read_hyperparameters( file_path=hyperparameters_file ) )
        fitnesses_dfs.append( read_fitnesses( file_path=fitnesses_file ) )

    union_hyperparameters_vs_balanced_accuracy_plots(
        hyperparameters_dfs=(
            hyperparameters_dfs
        ),
        fitnesses_dfs=fitnesses_dfs,
        plot_dir=plot_dir
    )

    final_hyperparameters_file = (
        hyperparameters_final_file(
            hof_dir=hof_dir
        )
    )

    final_fitnesses_file = (
        fitnesses_final_file(
            hof_dir=hof_dir
        )
    )

    if (
        final_hyperparameters_file
        is not None
        and final_fitnesses_file
        is not None
    ):

        final_hyperparameters_vs_balanced_accuracy_plots(
            hyperparameters_file=(
                final_hyperparameters_file
            ),
            fitnesses_file=(
                final_fitnesses_file
            ),
            plot_dir=plot_dir
        )


def hof_hyperparameter_accuracy_plots_every_hof(
        main_hofs_dir: str
):
    """
    Creates hyperparameter vs balanced accuracy
    plots for every HOF.

    For example:

        hofs/
        ├── pareto/
        ├── sum50/
        └── ...
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

        hof_hyperparameter_accuracy_plots_for_directory(
            hof_dir=hof_dir
        )