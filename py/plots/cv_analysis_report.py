import os
import sys
import argparse
import warnings

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, '..', '..'))
sys.path.append(os.path.join(_PROJECT_ROOT, 'py'))

from scratch.plot_interactive import get_data_from_exp, calculate_c_metric


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.getcwd(), "tuning_reports", "CV_Analysis")

DATASETS = [
    "brca",
    "luad_lusc",
    "tcga_kir",
    "tcga_ov",
]

DATASET_LABELS = {
    "brca": "TCGA-BRCA",
    "luad_lusc": "TCGA-LU",
    "tcga_kir": "TCGA-KI3",
    "tcga_ov": "TCGA-OV",
}

MODELS_MAP = {
    "naive_bayes": "NB_bal_acc_leanness",
    "svm":          "leanness_svm_bal_acc",
    "RF":           "RF_bal_acc_leanness",
    "logistic":     "leanness_logit100_bal_acc",
}

MODEL_LABELS = {
    "naive_bayes": "NB",
    "svm": "SVM",
    "RF": "RF",
    "logistic": "LR",
}


# Algoritmos utilizados en el TFG.
# MOABC se elimina completamente.
ALGOS = [
    "nsga2",
    "nsga2_ch",
    "nsga2_chs",
    "hpe_nsga2_chs",
]

ALGO_LABELS = {
    "nsga2":          "NSGA2",
    "nsga2_ch":       "NSGA2-CH",
    "nsga2_chs":      "NSGA2-CHS",
    "hpe_nsga2_chs":  "HPE-NSGA2-CHS",
}

ALGO_SHORT = {
    k: v.replace('\n', ' ')
    for k, v in ALGO_LABELS.items()
}

N_ALGO = len(ALGOS)

METRICS = [
    "schv",
    "j_div",
    "dice",
    "c_net",
]

METRIC_LABELS = [
    "Soft-CHV",
    "J_div (1-J)",
    "Dice",
    "C_net",
]


# ---------------------------------------------------------------------------
# Sensitivity scenarios
# ---------------------------------------------------------------------------

SCENARIOS = {
    "Balanced": [
        0.25,
        0.25,
        0.25,
        0.25,
    ],

    "Performance": [
        0.50,
        0.05,
        0.15,
        0.30,
    ],

    "Discovery": [
        0.35,
        0.25,
        0.15,
        0.25,
    ],

    "Reproducibility": [
        0.35,
        0.10,
        0.35,
        0.20,
    ],
}


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def get_obj_dir(dataset: str, model: str) -> str:
    return MODELS_MAP.get(model, "")


def big_params(model: str) -> dict:
    """
    Parameters used by the experiments.

    HPE uses:
      - 500 individuals for NB, SVM and RF.
      - 200 individuals for LR.
      - 1000 generations.
      - 3 inner folds.
      - 5 outer folds.
    """

    is_log = model == "logistic"

    return {
        "pop": 200 if is_log else 500,
        "gen": 1000,
        "inner_folds": 3,
        "outer_folds": 5,
    }


def get_expected_nsga_name(
    base_algo: str,
    pop: int,
    gen: int,
    inner_folds: int,
) -> str:

    k = inner_folds

    if base_algo == "nsga2":

        return (
            f"NSGA2_k{k}_pop{pop}_uni0-50_gen{gen}_"
            f"CrowdFull_c0.33_m1.0flip_(none,none)"
        )

    elif base_algo == "nsga2_ch":

        return (
            f"NSGA2_k{k}_pop{pop}_uni0-50_gen{gen}_"
            f"CrowdCI_c0.33_m1.0flip_(MV_lassoFI,none)"
        )

    elif base_algo == "nsga2_chs":

        return (
            f"NSGA2_k{k}_pop{pop}_uni0-50_gen{gen}_"
            f"CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)"
        )

    elif base_algo == "hpe_nsga2_chs":

        return (
            f"HPE_NSGA2_k{k}_pop{pop}_uni0-50_gen{gen}_"
            f"CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)"
        )

    return ""


def resolve_algo_dir(
    algo: str,
    pop: int,
    gen: int,
    inner_folds: int,
) -> str:

    if algo in (
        "nsga2",
        "nsga2_ch",
        "nsga2_chs",
        "hpe_nsga2_chs",
    ):
        return get_expected_nsga_name(
            algo,
            pop,
            gen,
            inner_folds,
        )

    return ""


def build_exp_path(
    dataset: str,
    model: str,
    algo: str,
    pop: int,
    gen: int,
    inner_folds: int,
    outer_folds: int,
) -> str:

    obj_dir = get_obj_dir(dataset, model)

    if not obj_dir:
        return ""

    algo_dir = resolve_algo_dir(
        algo,
        pop,
        gen,
        inner_folds,
    )

    if not algo_dir:
        return ""

    return os.path.join(
        os.getcwd(),
        dataset,
        "mrna",
        obj_dir,
        f"{outer_folds}_folds",
        algo_dir,
    )


def resolve_and_build(
    dataset: str,
    model: str,
    algo: str,
) -> str:

    p = big_params(model)

    return build_exp_path(
        dataset,
        model,
        algo,
        pop=p["pop"],
        gen=p["gen"],
        inner_folds=p["inner_folds"],
        outer_folds=p["outer_folds"],
    )


# ---------------------------------------------------------------------------
# C-metric
# ---------------------------------------------------------------------------

def compute_c_matrix(
    dataset: str,
    model: str,
) -> np.ndarray:

    """
    Return the global C-metric matrix.

    C(A,B) = fraction of solutions from B dominated by A.

    Rows = dominating algorithm A.
    Columns = dominated algorithm B.

    Diagonal = NaN.
    """

    mat = np.full(
        (N_ALGO, N_ALGO),
        np.nan,
    )

    paths = {}

    for algo in ALGOS:
        paths[algo] = resolve_and_build(
            dataset,
            model,
            algo,
        )

    for i, algo_a in enumerate(ALGOS):

        for j, algo_b in enumerate(ALGOS):

            if i == j:
                continue

            path_a = paths[algo_a]
            path_b = paths[algo_b]

            if (
                not os.path.isdir(path_a)
                or not os.path.isdir(path_b)
            ):
                continue

            data_a = get_data_from_exp(path_a)
            data_b = get_data_from_exp(path_b)

            if data_a is None or data_b is None:
                continue

            folds_a = data_a.get("folds", {})
            folds_b = data_b.get("folds", {})

            if not folds_a or not folds_b:
                continue

            xs_a = []
            ys_a = []

            xs_b = []
            ys_b = []

            for fold in folds_a.values():

                xs_a.extend(fold["x"])
                ys_a.extend(fold["y"])

            for fold in folds_b.values():

                xs_b.extend(fold["x"])
                ys_b.extend(fold["y"])

            if not xs_a or not xs_b:
                continue

            c_value = calculate_c_metric(
                np.array(xs_a),
                np.array(ys_a),
                np.array(xs_b),
                np.array(ys_b),
            )

            if not np.isnan(c_value):

                mat[i, j] = c_value

    return mat


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all_metrics() -> dict:

    """
    Load all metrics for all datasets, classifiers and algorithms.
    """

    result = {}

    for dataset in DATASETS:

        result[dataset] = {}

        for model in MODELS_MAP:

            result[dataset][model] = {}

            c_matrix = compute_c_matrix(
                dataset,
                model,
            )

            for algo_index, algo in enumerate(ALGOS):

                path = resolve_and_build(
                    dataset,
                    model,
                    algo,
                )

                if not os.path.isdir(path):
                    continue

                exp = get_data_from_exp(path)

                if exp is None:
                    continue

                metrics = exp.get(
                    "metrics",
                    {},
                )

                jaccard_raw = metrics.get(
                    "var_m",
                    np.nan,
                )

                schv = metrics.get(
                    "schv_m",
                    np.nan,
                )

                dice = metrics.get(
                    "dice_m",
                    np.nan,
                )

                # C values where this algorithm dominates another.
                c_out_values = [
                    c_matrix[algo_index, j]
                    for j in range(N_ALGO)
                    if (
                        j != algo_index
                        and not np.isnan(
                            c_matrix[algo_index, j]
                        )
                    )
                ]

                c_out = (
                    float(np.mean(c_out_values))
                    if c_out_values
                    else np.nan
                )

                # C values where another algorithm dominates this one.
                c_in_values = [
                    c_matrix[j, algo_index]
                    for j in range(N_ALGO)
                    if (
                        j != algo_index
                        and not np.isnan(
                            c_matrix[j, algo_index]
                        )
                    )
                ]

                c_in = (
                    float(np.mean(c_in_values))
                    if c_in_values
                    else np.nan
                )

                c_net = (
                    c_out - c_in
                    if (
                        not np.isnan(c_out)
                        and not np.isnan(c_in)
                    )
                    else np.nan
                )

                result[dataset][model][algo] = {

                    "schv": schv,

                    "jaccard": jaccard_raw,

                    "j_div": (
                        1.0 - jaccard_raw
                        if not np.isnan(jaccard_raw)
                        else np.nan
                    ),

                    "dice": dice,

                    "c_out": c_out,

                    "c_in": c_in,

                    "c_net": c_net,
                }

    return result


# ---------------------------------------------------------------------------
# Rank normalization
# ---------------------------------------------------------------------------

def rank_normalize(values: list) -> np.ndarray:

    """
    Assign rank 1..n, where rank 1 is best.

    Returned score:
        (n - rank) / (n - 1)

    Therefore:
        best = 1
        worst = 0
    """

    arr = np.array(
        values,
        dtype=float,
    )

    valid_mask = ~np.isnan(arr)

    n = len(arr)

    scores = np.full(
        n,
        np.nan,
    )

    if valid_mask.sum() == 0:
        return scores

    valid_values = arr[valid_mask]

    # All metrics are treated as "higher is better".
    order = np.argsort(
        valid_values
    )[::-1]

    ranks = np.empty_like(
        valid_values
    )

    ranks[order] = np.arange(
        1,
        len(valid_values) + 1,
    )

    scores[valid_mask] = (
        len(valid_values) - ranks
    ) / max(
        1,
        len(valid_values) - 1,
    )

    return scores


def compute_rank_scores(raw: dict) -> dict:

    """
    Compute rank scores independently for each
    dataset, classifier and metric.
    """

    result = {}

    for dataset in DATASETS:

        result[dataset] = {}

        for model in MODELS_MAP:

            result[dataset][model] = {}

            for metric in METRICS:

                values = []

                for algo in ALGOS:

                    entry = raw[
                        dataset
                    ][
                        model
                    ].get(algo)

                    if entry is None:

                        values.append(np.nan)

                    else:

                        values.append(
                            entry.get(
                                metric,
                                np.nan,
                            )
                        )

                rank_scores = rank_normalize(
                    values
                )

                for algo_index, algo in enumerate(ALGOS):

                    if algo not in result[dataset][model]:

                        result[
                            dataset
                        ][
                            model
                        ][
                            algo
                        ] = {}

                    result[
                        dataset
                    ][
                        model
                    ][
                        algo
                    ][
                        metric + "_rank"
                    ] = rank_scores[
                        algo_index
                    ]

    return result


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_ranks(
    ranked: dict,
) -> np.ndarray:

    """
    Aggregate normalized rank scores across
    classifiers and datasets.

    Returns:
        (N_ALGO, 4)
    """

    per_dataset = np.full(
        (
            len(DATASETS),
            N_ALGO,
            len(METRICS),
        ),
        np.nan,
    )

    for dataset_index, dataset in enumerate(DATASETS):

        for algo_index, algo in enumerate(ALGOS):

            for metric_index, metric in enumerate(METRICS):

                values = []

                for model in MODELS_MAP:

                    value = ranked[
                        dataset
                    ][
                        model
                    ].get(
                        algo,
                        {},
                    ).get(
                        metric + "_rank",
                        np.nan,
                    )

                    if not np.isnan(value):

                        values.append(value)

                if values:

                    per_dataset[
                        dataset_index,
                        algo_index,
                        metric_index,
                    ] = float(
                        np.mean(values)
                    )

    return np.nanmean(
        per_dataset,
        axis=0,
    )


# ---------------------------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------------------------

def sensitivity_analysis(
    aggregated: np.ndarray,
) -> pd.DataFrame:

    """
    Compute a composite score for every algorithm
    under each weighting scenario.
    """

    rows = []

    for scenario_name, weights in SCENARIOS.items():

        weights_array = np.array(
            weights
        )

        scores = aggregated @ weights_array

        for algo_index, algo in enumerate(ALGOS):

            rows.append({
                "Algorithm": ALGO_SHORT[algo],
                "Scenario": scenario_name,
                "CompositeScore": scores[algo_index],
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Breakdowns
# ---------------------------------------------------------------------------

def breakdown_by_dataset(
    ranked: dict,
) -> pd.DataFrame:

    """
    Produce one balanced composite score per
    dataset and algorithm.
    """

    rows = []

    for dataset in DATASETS:

        for algo in ALGOS:

            metric_values = []

            for metric in METRICS:

                values = [
                    ranked[
                        dataset
                    ][
                        model
                    ].get(
                        algo,
                        {},
                    ).get(
                        metric + "_rank",
                        np.nan,
                    )
                    for model in MODELS_MAP
                ]

                if not np.all(
                    np.isnan(values)
                ):

                    metric_values.append(
                        np.nanmean(values)
                    )

                else:

                    metric_values.append(
                        np.nan
                    )

            score = (
                np.nanmean(metric_values)
                if not np.all(
                    np.isnan(metric_values)
                )
                else np.nan
            )

            rows.append({
                "Dataset": DATASET_LABELS.get(
                    dataset,
                    dataset,
                ),
                "Algorithm": ALGO_SHORT[algo],
                "Score": score,
            })

    return pd.DataFrame(rows)


def breakdown_by_algo_classifier(
    ranked: dict,
) -> pd.DataFrame:

    """
    Produce a score for every algorithm/classifier
    combination, averaged across datasets.
    """

    rows = []

    for algo in ALGOS:

        for model in MODELS_MAP:

            metric_vectors = []

            for dataset in DATASETS:

                entry = ranked[
                    dataset
                ][
                    model
                ].get(
                    algo,
                    {},
                )

                vector = np.array([
                    entry.get(
                        metric + "_rank",
                        np.nan,
                    )
                    for metric in METRICS
                ])

                if not np.all(
                    np.isnan(vector)
                ):

                    metric_vectors.append(
                        vector
                    )

            if metric_vectors:

                average_vector = np.nanmean(
                    metric_vectors,
                    axis=0,
                )

                score = np.nanmean(
                    average_vector
                )

            else:

                score = np.nan

            rows.append({
                "Algorithm": ALGO_SHORT[algo],
                "Classifier": MODEL_LABELS[model],
                "Score": score,
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def friedman_nemenyi_test(
    raw: dict,
) -> str:

    """
    Friedman test for each metric, followed by
    Nemenyi post-hoc test when significant.
    """

    lines = []

    try:

        from scipy.stats import friedmanchisquare
        import scikit_posthocs as sp

    except ImportError:

        lines.append(
            "scipy.stats or scikit_posthocs not available."
        )

        return "\n".join(lines)

    for metric_index, metric in enumerate(METRICS):

        lines.append(
            f"\n{'=' * 60}"
        )

        lines.append(
            f" Metric: {METRIC_LABELS[metric_index]}"
        )

        lines.append(
            f"{'=' * 60}"
        )

        algo_values = {
            algo: []
            for algo in ALGOS
        }

        for dataset in DATASETS:

            for model in MODELS_MAP:

                for algo in ALGOS:

                    value = raw[
                        dataset
                    ][
                        model
                    ].get(
                        algo,
                        {},
                    ).get(
                        metric,
                        np.nan,
                    )

                    algo_values[
                        algo
                    ].append(
                        value
                    )

        data = [
            np.array(
                algo_values[algo]
            )
            for algo in ALGOS
        ]

        # Keep complete paired observations only.
        complete_mask = np.ones(
            len(DATASETS) * len(MODELS_MAP),
            dtype=bool,
        )

        for values in data:

            complete_mask &= ~np.isnan(values)

        if complete_mask.sum() < 3:

            lines.append(
                "  Insufficient complete paired data for Friedman test."
            )

            continue

        data_complete = [
            values[complete_mask]
            for values in data
        ]

        try:

            statistic, p_value = friedmanchisquare(
                *data_complete
            )

            lines.append(
                f"  Friedman chi2 = {statistic:.4f}, "
                f"p = {p_value:.6f}"
            )

            if p_value < 0.05:

                lines.append(
                    "  -> Significant differences detected (p<0.05)"
                )

                # FIX: usar data_complete (arrays ya enmascarados),
                # no algo_values[algo] (lista de Python, que no admite
                # indexado con una máscara booleana de numpy).
                df = pd.DataFrame({
                    ALGO_SHORT[algo]: data_complete[algo_index]
                    for algo_index, algo in enumerate(ALGOS)
                })

                try:

                    nemenyi = (
                        sp.posthoc_nemenyi_friedman(df)
                    )

                    lines.append(
                        "  Nemenyi post-hoc (p-values):"
                    )

                    lines.append(
                        f"  {'':>20s}"
                        + "".join(
                            f"{ALGO_SHORT[a]:>20s}"
                            for a in ALGOS
                        )
                    )

                    for algo_a in ALGOS:

                        row = (
                            f"  "
                            f"{ALGO_SHORT[algo_a]:>20s}"
                        )

                        for algo_b in ALGOS:

                            # FIX: f-string partida en trozos con las
                            # llaves separadas -> unificada en una sola.
                            row += (
                                f"{nemenyi.loc[ALGO_SHORT[algo_a], ALGO_SHORT[algo_b]]:>20.4f}"
                            )

                        lines.append(row)

                except Exception as error:

                    lines.append(
                        f"  Nemenyi failed: {error}"
                    )

            else:

                lines.append(
                    "  -> No significant differences."
                )

        except Exception as error:

            lines.append(
                f"  Test failed: {error}"
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------

def plot_sensitivity_heatmap(
    sensitivity_df: pd.DataFrame,
):

    """
    Heatmap:
        algorithm × scenario
    """

    pivot = sensitivity_df.pivot_table(
        index="Algorithm",
        columns="Scenario",
        values="CompositeScore",
    )

    scenario_order = list(
        SCENARIOS.keys()
    )

    pivot = pivot[
        scenario_order
    ]

    algo_order = [
        ALGO_SHORT[algo]
        for algo in ALGOS
    ]

    pivot = pivot.loc[
        algo_order
    ]

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".3f",
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        ax=ax,
        linewidths=1,
        linecolor="gray",
        cbar_kws={
            "label": "Composite Score"
        },
    )

    ax.set_title(
        "Sensitivity Analysis — Algorithm × Scenario",
        fontsize=13,
        fontweight="bold",
    )

    ax.set_ylabel("")
    ax.set_xlabel("")

    plt.tight_layout()

    path = os.path.join(
        OUTPUT_DIR,
        "sensitivity_heatmap.png",
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"  [SAVED] {path}"
    )


def plot_radar(
    aggregated: np.ndarray,
):

    """
    Radar chart:
        algorithm × metric
    """

    n_metrics = len(
        METRICS
    )

    angles = np.linspace(
        0,
        2 * np.pi,
        n_metrics,
        endpoint=False,
    ).tolist()

    angles += angles[:1]

    colors = plt.cm.Set1(
        np.linspace(
            0,
            1,
            N_ALGO,
        )
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw={
            "polar": True
        },
    )

    for algo_index, algo in enumerate(ALGOS):

        values = aggregated[
            algo_index
        ].tolist()

        values += values[:1]

        ax.plot(
            angles,
            values,
            "o-",
            color=colors[algo_index],
            linewidth=2,
            label=ALGO_SHORT[algo],
        )

        ax.fill(
            angles,
            values,
            alpha=0.1,
            color=colors[algo_index],
        )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        METRIC_LABELS,
        fontsize=11,
        fontweight="bold",
    )

    ax.set_ylim(
        0,
        1,
    )

    ax.set_yticks([
        0.2,
        0.4,
        0.6,
        0.8,
        1.0,
    ])

    ax.set_yticklabels([
        "0.2",
        "0.4",
        "0.6",
        "0.8",
        "1.0",
    ], fontsize=8)

    ax.set_title(
        "Algorithm Profile Radar — Aggregated Rank Scores",
        fontsize=13,
        fontweight="bold",
        pad=20,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.3, 1.1),
        fontsize=9,
    )

    plt.tight_layout()

    path = os.path.join(
        OUTPUT_DIR,
        "radar_profiles.png",
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"  [SAVED] {path}"
    )


def plot_cnet_heatmap(
    raw: dict,
):

    """
    C_net values for every dataset/classifier/algorithm.
    """

    n_datasets = len(
        DATASETS
    )

    n_models = len(
        MODELS_MAP
    )

    grid = np.full(
        (
            n_datasets,
            n_models,
            N_ALGO,
        ),
        np.nan,
    )

    for dataset_index, dataset in enumerate(DATASETS):

        for model_index, model in enumerate(MODELS_MAP):

            for algo_index, algo in enumerate(ALGOS):

                entry = raw[
                    dataset
                ][
                    model
                ].get(
                    algo
                )

                if (
                    entry is not None
                    and not np.isnan(
                        entry.get(
                            "c_net",
                            np.nan,
                        )
                    )
                ):

                    grid[
                        dataset_index,
                        model_index,
                        algo_index,
                    ] = entry[
                        "c_net"
                    ]

    fig, axes = plt.subplots(
        n_datasets,
        n_models,
        figsize=(
            3.5 * n_models,
            2.8 * n_datasets,
        ),
        squeeze=False,
    )

    for dataset_index, dataset in enumerate(DATASETS):

        for model_index, model in enumerate(MODELS_MAP):

            ax = axes[
                dataset_index,
                model_index,
            ]

            values = grid[
                dataset_index,
                model_index,
                :,
            ]

            matrix = values.reshape(
                1,
                -1,
            )

            annotations = np.array([
                [
                    (
                        f"{value:.3f}"
                        if not np.isnan(value)
                        else ""
                    )
                    for value in values
                ]
            ])

            sns.heatmap(
                matrix,
                annot=annotations,
                fmt="",
                cmap="RdYlGn",
                vmin=-0.5,
                vmax=0.5,
                xticklabels=[
                    ALGO_SHORT[algo]
                    for algo in ALGOS
                ],
                yticklabels=False,
                ax=ax,
                linewidths=1,
                linecolor="gray",
                cbar=False,
            )

            if dataset_index == 0:

                ax.set_title(
                    MODEL_LABELS[model],
                    fontsize=9,
                    fontweight="bold",
                )

            if model_index == 0:

                ax.set_ylabel(
                    DATASET_LABELS.get(
                        dataset,
                        dataset,
                    ),
                    fontsize=9,
                    fontweight="bold",
                )

    # Single shared colorbar.
    cbar_ax = fig.add_axes([
        0.92,
        0.12,
        0.012,
        0.75,
    ])

    scalar_mappable = plt.cm.ScalarMappable(
        cmap="RdYlGn",
        norm=plt.Normalize(
            -0.5,
            0.5,
        ),
    )

    scalar_mappable.set_array([])

    fig.colorbar(
        scalar_mappable,
        cax=cbar_ax,
        label="C_net",
    )

    fig.suptitle(
        "C_net (C_out - C_in) per "
        "(Dataset, Classifier, Algorithm)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    plt.tight_layout(
        rect=[
            0,
            0,
            0.90,
            0.95,
        ]
    )

    path = os.path.join(
        OUTPUT_DIR,
        "cnet_heatmap.png",
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"  [SAVED] {path}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="CV Analysis Report"
    )

    parser.parse_args()

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    print(
        f"\n{'=' * 65}"
    )

    print(
        " CV ANALYSIS REPORT — HPE"
    )

    print(
        f"  Output: {OUTPUT_DIR}"
    )

    print(
        f"{'=' * 65}\n"
    )

    print(
        "[1/6] Loading metrics for all combinations..."
    )

    raw = load_all_metrics()

    print(
        "[2/6] Computing rank-based normalization..."
    )

    ranked = compute_rank_scores(
        raw
    )

    print(
        "[3/6] Aggregating across classifiers and datasets..."
    )

    aggregated = aggregate_ranks(
        ranked
    )

    print(
        "  Aggregated scores (algo × metric):"
    )

    print(
        f"  {'Algo':>20s}"
        + "".join(
            f"{label:>12s}"
            for label in METRIC_LABELS
        )
    )

    for algo_index, algo in enumerate(ALGOS):

        row = (
            f"  "
            f"{ALGO_SHORT[algo]:>20s}"
        )

        for metric_index in range(
            len(METRICS)
        ):

            # FIX: f-string partida en trozos -> unificada en una sola.
            row += (
                f"{aggregated[algo_index, metric_index]:>12.4f}"
            )

        print(row)

    print(
        "[4/6] Sensitivity analysis..."
    )

    sensitivity_df = sensitivity_analysis(
        aggregated
    )

    sensitivity_pivot = sensitivity_df.pivot_table(
        index="Algorithm",
        columns="Scenario",
        values="CompositeScore",
    )

    scenario_order = list(
        SCENARIOS.keys()
    )

    sensitivity_pivot = sensitivity_pivot[
        scenario_order
    ]

    print(
        "  Composite Scores:"
    )

    algorithm_order = (
        sensitivity_pivot.mean(
            axis=1
        ).sort_values(
            ascending=False
        ).index
    )

    print(
        f"  {'Algo':>20s}"
        + "".join(
            f"{scenario:>18s}"
            for scenario in scenario_order
        )
    )

    for algorithm in algorithm_order:

        row = (
            f"  "
            f"{algorithm:>20s}"
        )

        for scenario in scenario_order:

            # FIX: f-string partida en trozos -> unificada en una sola.
            row += (
                f"{sensitivity_pivot.loc[algorithm, scenario]:>18.4f}"
            )

        print(row)

    sensitivity_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "sensitivity_analysis.csv",
        ),
        index=False,
    )

    print(
        "  [SAVED] sensitivity_analysis.csv"
    )

    print(
        "[5/6] Breakdowns..."
    )

    breakdown_dataset = breakdown_by_dataset(
        ranked
    )

    breakdown_dataset.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "breakdown_by_dataset.csv",
        ),
        index=False,
    )

    print(
        "  [SAVED] breakdown_by_dataset.csv"
    )

    breakdown_classifier = breakdown_by_algo_classifier(
        ranked
    )

    breakdown_classifier.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "breakdown_by_algo_classifier.csv",
        ),
        index=False,
    )

    print(
        "  [SAVED] breakdown_by_algo_classifier.csv"
    )

    print(
        "[6/6] Statistical tests..."
    )

    report = friedman_nemenyi_test(
        raw
    )

    report_path = os.path.join(
        OUTPUT_DIR,
        "statistical_tests_report.txt",
    )

    with open(
        report_path,
        "w",
    ) as file:

        file.write(
            report
        )

    print(
        f"  [SAVED] {report_path}"
    )

    print(
        "\nGenerating visualizations..."
    )

    plot_sensitivity_heatmap(
        sensitivity_df
    )

    plot_cnet_heatmap(
        raw
    )

    plot_radar(
        aggregated
    )

    print(
        f"\nDone. All outputs in "
        f"{OUTPUT_DIR}\n"
    )



if __name__ == "__main__":
    main()