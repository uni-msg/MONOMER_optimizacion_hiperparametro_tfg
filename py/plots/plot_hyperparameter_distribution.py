#!/usr/bin/env python3
"""
MONOMER - Hyperparameter distribution analysis

What this script produces
-------------------------
For each classifier, it creates UN PDF que contiene varios gráficos:
    - one graph/subplot per MUTABLE hyperparameter;
    - all 5 outer-CV folds are combined for each dataset;
    - each dataset has its own color;
    - the distribution therefore shows how that hyperparameter evolved
      across all folds and all Pareto solutions.

Fixed/non-mutable hyperparameters are automatically ignored:
    - if a hyperparameter has only one unique value across ALL available
      datasets/folds, no graph is generated for it.

The four classifiers are analyzed independently:
    naive_bayes
    svm
    RF
    logistic

Only:
    solution_hyperparameters_fold_0.csv ... fold_4.csv
    solution_fitnesses_fold_0.csv ... fold_4.csv

are considered. *_final.csv files are NEVER used.

Output:
    work/tuning_reports/hyperparameters_distribution/
        naive_bayes_hyperparameters_distribution.png
        svm_hyperparameters_distribution.png
        RF_hyperparameters_distribution.png
        logistic_hyperparameters_distribution.png

Además, se generan PDF individuales for each mutable
hyperparameter. This makes it easy to reuse them separately if desired.
"""

import os
import re
import argparse
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# ============================================================================
# CONFIGURATION
# ============================================================================

DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]

DATASET_LABELS = {
    "brca": "BRCA",
    "luad_lusc": "LUAD-LUSC",
    "tcga_kir": "KIR",
    "tcga_ov": "OV",
}

MODELS = {
    "naive_bayes": "NB_bal_acc_leanness",
    "svm": "leanness_svm_bal_acc",
    "RF": "RF_bal_acc_leanness",
    "logistic": "leanness_logit100_bal_acc",
}

MODEL_LABELS = {
    "naive_bayes": "Naive Bayes",
    "svm": "SVM",
    "RF": "Random Forest",
    "logistic": "Logistic Regression",
}

N_FOLDS = 5

DATASET_COLORS = {     "brca": "#1f77b4",     "luad_lusc": "#ff7f0e",     "tcga_kir": "#2ca02c",     "tcga_ov": "#d62728", } 

# ============================================================================
# PATHS
# ============================================================================

def find_experiment_path(work_dir, dataset, model_dir):
    """
    Find the HPE experiment under:
        dataset/mrna/model_dir/5_folds/

    If several HPE_NSGA2 directories exist, prefer the one containing the
    greatest number of the expected fold hyperparameter files.
    """
    base = os.path.join(
        work_dir,
        dataset,
        "mrna",
        model_dir,
        "5_folds",
    )

    if not os.path.isdir(base):
        return None

    candidates = []

    for name in os.listdir(base):
        path = os.path.join(base, name)

        if not os.path.isdir(path):
            continue

        if not name.startswith("HPE_NSGA2"):
            continue

        pareto = os.path.join(path, "hofs", "Pareto")
        score = 0

        for fold in range(N_FOLDS):
            hp = os.path.join(
                pareto,
                f"solution_hyperparameters_fold_{fold}.csv",
            )
            if os.path.isfile(hp):
                score += 1

        candidates.append((score, path))

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (-item[0], item[1])
    )

    return candidates[0][1]


def hyperparameter_file(exp_path, fold):
    """
    Construct the exact fold filename.

    This intentionally does NOT use glob(), so *_final.csv can never
    accidentally enter the analysis.
    """
    return os.path.join(
        exp_path,
        "hofs",
        "Pareto",
        f"solution_hyperparameters_fold_{fold}.csv",
    )


# ============================================================================
# DATA LOADING
# ============================================================================

def load_dataset(experiment_path, dataset):
    frames = []

    for fold in range(N_FOLDS):
        path = hyperparameter_file(experiment_path, fold)

        if not os.path.isfile(path):
            print(
                f"      [WARN] {dataset.upper()} fold {fold}: "
                f"file not found"
            )
            continue

        try:
            df = pd.read_csv(path)
        except Exception as exc:
            print(
                f"      [WARN] {dataset.upper()} fold {fold}: "
                f"could not read CSV: {exc}"
            )
            continue

        if df.empty:
            continue

        df = df.copy()
        df["_fold"] = fold
        df["_dataset"] = dataset

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# ============================================================================
# COLUMN IDENTIFICATION
# ============================================================================

def is_metadata_column(column):
    """
    Columns that are not hyperparameters.

    The actual solution_hyperparameters files can contain additional
    bookkeeping columns. We exclude them here.
    """
    name = str(column).strip().lower()

    metadata_tokens = [
        "solution",
        "fitness",
        "objective",
        "balanced_accuracy",
        "bal_acc",
        "leanness",
        "fold",
        "index",
        "unnamed:",
        "rank",
        "crowding",
    ]

    return any(token in name for token in metadata_tokens)


def get_hyperparameter_columns(df):
    return [
        column
        for column in df.columns
        if not str(column).startswith("_")
        and not is_metadata_column(column)
    ]


# ============================================================================
# VALUE / TYPE HELPERS
# ============================================================================

def as_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def classify_type(series):
    """
    Return:
        boolean
        integer
        float
        categorical
    """
    values = series.dropna()

    if values.empty:
        return "categorical"

    strings = values.astype(str).str.strip().str.lower()

    if strings.isin(
        ["true", "false", "yes", "no", "0", "1"]
    ).all():
        return "boolean"

    numeric = pd.to_numeric(values, errors="coerce")

    if numeric.notna().all():
        arr = numeric.to_numpy(dtype=float)

        if np.allclose(arr, np.round(arr)):
            return "integer"

        return "float"

    return "categorical"


def unique_values(series):
    """
    Count actual different values robustly.
    """
    values = series.dropna()

    if values.empty:
        return []

    numeric = pd.to_numeric(values, errors="coerce")

    if numeric.notna().all():
        return sorted(
            np.unique(numeric.to_numpy(dtype=float)).tolist()
        )

    return sorted(
        values.astype(str).unique().tolist()
    )


def is_mutable(df, column):
    """
    A parameter is considered mutable only if it takes at least two
    different values in the complete analysis.

    This is exactly what is wanted for fixed parameters: if the parameter
    never changes across all datasets/folds/solutions, no graph is created.
    """
    return len(unique_values(df[column])) > 1


def looks_log_scale(series):
    """
    Detect parameters spanning several orders of magnitude.

    This is only used for visualization. It does not change the values.
    """
    values = as_numeric(series).dropna()

    if len(values) < 5:
        return False

    arr = np.abs(values.to_numpy(dtype=float))
    arr = arr[np.isfinite(arr)]

    if len(arr) < 5 or np.any(arr <= 0):
        return False

    ratio = arr.max() / arr.min()

    return ratio >= 100


def pretty_name(name):
    text = str(name).replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ============================================================================
# PLOT HELPERS
# ============================================================================

def get_dataset_values(df, column, dataset):
    subset = df.loc[df["_dataset"] == dataset, column].dropna()

    if subset.empty:
        return subset

    kind = classify_type(df[column])

    if kind in {"float", "integer"}:
        return as_numeric(subset).dropna()

    return subset.astype(str)


def plot_numeric_distribution(ax, df, column):
    """
    One distribution graph:
        x-axis = dataset
        y-axis = hyperparameter value

    Every point is one Pareto solution from one of the five folds.
    Dataset color is constant, so the five folds are visually combined.
    """
    datasets_present = [
        dataset
        for dataset in DATASETS
        if (df["_dataset"] == dataset).any()
    ]

    positions = np.arange(len(datasets_present)) + 1

    all_values = []

    for dataset in datasets_present:
        values = get_dataset_values(df, column, dataset)

        if values.empty:
            continue

        all_values.append(values.to_numpy(dtype=float))

    # Violin gives the overall distribution, while points show the actual
    # evolved values.
    if all(
        len(values) >= 2
        for values in all_values
    ):
        violin = ax.violinplot(
            all_values,
            positions=positions,
            showmeans=False,
            showmedians=False,
            showextrema=True,
        )

        # The violin halo uses the same color as the corresponding dataset samples.
        for body, dataset in zip(violin["bodies"], datasets_present):
            color = DATASET_COLORS[dataset]
            body.set_facecolor(color)
            body.set_edgecolor(color)
            body.set_alpha(0.20)

        # Violin extrema are neutral gray.
        for key in ("cmins", "cmaxes", "cbars"):
            if key in violin:
                violin[key].set_color("#555555")
                violin[key].set_alpha(0.55)

    for i, dataset in enumerate(datasets_present):
        values = get_dataset_values(df, column, dataset)

        if values.empty:
            continue

        values = values.to_numpy(dtype=float)

        rng = np.random.default_rng(
            1000 + DATASETS.index(dataset)
        )

        # Small horizontal jitter prevents points from being completely
        # hidden when many solutions share the same value.
        x = np.full(len(values), i + 1, dtype=float)
        x += rng.normal(0, 0.045, size=len(values))

        ax.scatter(
            x,
            values,
            s=14,
            alpha=0.32,
            label=DATASET_LABELS[dataset],
        )

    ax.set_xticks(positions)
    ax.set_xticklabels(
        [DATASET_LABELS[d] for d in datasets_present]
    )

    ax.set_xlabel("Dataset")
    ax.set_ylabel(pretty_name(column))

    if looks_log_scale(df[column]):
        ax.set_yscale("log")
        ax.set_ylabel(
            f"{pretty_name(column)} (escala logarítmica)"
        )

    ax.grid(
        True,
        axis="y",
        linestyle=":",
        alpha=0.35,
    )

    ax.set_title(
        pretty_name(column),
        fontweight="bold",
    )


def plot_categorical_distribution(ax, df, column):
    """
    Categorical / boolean parameters are represented as proportions per
    dataset rather than pretending that categories have numeric distances.
    """
    datasets_present = [
        dataset
        for dataset in DATASETS
        if (df["_dataset"] == dataset).any()
    ]

    temp = df[["_dataset", column]].dropna().copy()
    temp[column] = temp[column].astype(str)

    categories = sorted(
        temp[column].unique().tolist()
    )

    if not categories:
        ax.text(
            0.5,
            0.5,
            "No usable values",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        return

    x = np.arange(len(datasets_present))

    width = 0.8 / len(categories)

    for category_index, category in enumerate(categories):
        proportions = []

        for dataset in datasets_present:
            values = temp.loc[
                temp["_dataset"] == dataset,
                column,
            ]

            if len(values) == 0:
                proportions.append(0.0)
            else:
                proportions.append(
                    (values == category).mean()
                )

        offset = (
            category_index
            - (len(categories) - 1) / 2
        ) * width

        bars = ax.bar(
            x + offset,
            proportions,
            width=width,
            alpha=0.75,
            label=str(category),
        )

        # Put percentage labels only when the number of categories is small.
        if len(categories) <= 5:
            for bar, proportion in zip(
                bars, proportions
            ):
                if proportion > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        proportion + 0.015,
                        f"{proportion:.0%}",
                        ha="center",
                        va="bottom",
                        fontsize=7,
                    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [DATASET_LABELS[d] for d in datasets_present]
    )

    ax.set_xlabel("Dataset")
    ax.set_ylabel("Proporción de soluciones de Pareto")
    ax.set_ylim(0, 1.12)

    if len(categories) <= 10:
        ax.legend(
            title=pretty_name(column),
            fontsize=8,
        )

    ax.grid(
        True,
        axis="y",
        linestyle=":",
        alpha=0.35,
    )

    ax.set_title(
        pretty_name(column),
        fontweight="bold",
    )


def plot_hyperparameter(ax, df, column):
    kind = classify_type(df[column])

    if kind in {"float", "integer"}:
        plot_numeric_distribution(
            ax,
            df,
            column,
        )
    else:
        plot_categorical_distribution(
            ax,
            df,
            column,
        )


# ============================================================================
# OUTPUT
# ============================================================================

def make_classifier_png(
    df,
    model,
    output_dir,
):
    """
    Create the requested combined PNG:
        one subplot per mutable hyperparameter.
    """
    model_label = MODEL_LABELS[model]

    hyperparameters = get_hyperparameter_columns(df)

    mutable = [
        column
        for column in hyperparameters
        if is_mutable(df, column)
    ]

    fixed = [
        column
        for column in hyperparameters
        if not is_mutable(df, column)
    ]

    print(
        f"    Hyperparameters found: {len(hyperparameters)}"
    )

    if fixed:
        print(
            "    Fixed parameters ignored: "
            + ", ".join(map(str, fixed))
        )

    print(
        "    Mutable parameters: "
        + (
            ", ".join(map(str, mutable))
            if mutable
            else "NONE"
        )
    )

    if not mutable:
        print(
            "    [!] Nothing to plot: all hyperparameters "
            "are fixed."
        )
        return

    # ------------------------------------------------------------------
    # Number of subplots.
    # ------------------------------------------------------------------
    n = len(mutable)

    if n == 1:
        ncols = 1
    elif n == 2:
        ncols = 2
    elif n <= 6:
        ncols = 2
    else:
        ncols = 3

    nrows = int(np.ceil(n / ncols))

    # Large enough that each individual graph remains readable.
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(7.0 * ncols, 5.2 * nrows),
        squeeze=False,
    )

    axes = axes.ravel()

    fig.suptitle(
        f"{model_label} — Distribución de hiperparámetros",
        fontsize=17,
        fontweight="bold",
        y=0.995,
    )

    for ax, column in zip(axes, mutable):
        plot_hyperparameter(
            ax,
            df,
            column,
        )

    # Hide unused subplot positions.
    for ax in axes[len(mutable):]:
        ax.axis("off")

    fig.tight_layout(
        rect=[0, 0, 1, 0.95]
    )

    combined_path = os.path.join(
        output_dir,
        f"{model}_hyperparameters_distribution.pdf",
    )

    fig.savefig(
        combined_path,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"    [SAVED] {combined_path}"
    )

    # ------------------------------------------------------------------
    # Also save each mutable hyperparameter individually.
    # ------------------------------------------------------------------
    individual_dir = os.path.join(
        output_dir,
        "individual",
        model,
    )

    os.makedirs(
        individual_dir,
        exist_ok=True,
    )

    for column in mutable:
        fig, ax = plt.subplots(
            figsize=(10, 7)
        )

        plot_hyperparameter(
            ax,
            df,
            column,
        )

        fig.suptitle(
            f"{model_label} — {pretty_name(column)}",
            fontsize=15,
            fontweight="bold",
        )

        fig.tight_layout(
            rect=[0, 0, 1, 0.95]
        )

        safe_name = re.sub(
            r"[^A-Za-z0-9_.-]+",
            "_",
            str(column),
        )

        individual_path = os.path.join(
            individual_dir,
            f"{safe_name}_distribution.pdf",
        )

        fig.savefig(
            individual_path,
            dpi=220,
            bbox_inches="tight",
        )

        plt.close(fig)


# ============================================================================
# MAIN
# ============================================================================

def analyze_model(
    work_dir,
    model,
    output_dir,
):
    model_dir = MODELS[model]
    model_label = MODEL_LABELS[model]

    print("\n" + "=" * 75)
    print(f" {model_label}")
    print("=" * 75)

    all_frames = []

    for dataset in DATASETS:
        print(f"\n  {dataset.upper()}")

        experiment_path = find_experiment_path(
            work_dir,
            dataset,
            model_dir,
        )

        if experiment_path is None:
            print(
                "    [-] HPE experiment not found"
            )
            continue

        print(
            f"    Experiment: {experiment_path}"
        )

        df = load_dataset(
            experiment_path,
            dataset,
        )

        if df.empty:
            print(
                "    [-] No fold data found"
            )
            continue

        print(
            f"    Solutions loaded: {len(df)}"
        )

        print(
            f"    Folds: "
            f"{sorted(df['_fold'].unique().tolist())}"
        )

        all_frames.append(df)

    if not all_frames:
        print(
            f"\n  [!] No data available for {model_label}"
        )
        return

    combined = pd.concat(
        all_frames,
        ignore_index=True,
    )

    make_classifier_png(
        combined,
        model,
        output_dir,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate hyperparameter distribution plots "
            "for MONOMER HPE experiments."
        )
    )

    parser.add_argument(
        "--work-dir",
        default=os.getcwd(),
        help=(
            "MONOMER work/ directory. "
            "Default: current directory."
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Output directory. "
            "Default: work/tuning_reports/"
            "hyperparameters_distribution"
        ),
    )

    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default=None,
        help=(
            "Analyze only one classifier. "
            "Default: all four."
        ),
    )

    args = parser.parse_args()

    work_dir = os.path.abspath(
        args.work_dir
    )

    if args.output_dir:
        output_dir = os.path.abspath(
            args.output_dir
        )
    else:
        output_dir = os.path.join(
            work_dir,
            "tuning_reports",
            "hyperparameters_distribution",
        )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    models = (
        [args.model]
        if args.model
        else list(MODELS.keys())
    )

    print("\n" + "=" * 75)
    print(" MONOMER — HYPERPARAMETER DISTRIBUTION")
    print("=" * 75)
    print(f"Work directory : {work_dir}")
    print(f"Output         : {output_dir}")
    print("Conjuntos      : BRCA, LUAD-LUSC, KIR, OV")
    print("Data           : outer folds 0, 1, 2, 3, 4 ONLY")
    print("Final files    : EXCLUDED")
    print("Fixed params   : EXCLUDED")
    print("=" * 75)

    for model in models:
        analyze_model(
            work_dir,
            model,
            output_dir,
        )

    print("\n" + "=" * 75)
    print(" DONE")
    print("=" * 75)
    print(
        f"PDF files generated in:\n{output_dir}"
    )


if __name__ == "__main__":
    main()
