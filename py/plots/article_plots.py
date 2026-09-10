"""Article plots for MONOMER Big CV.

Reads raw Big CV results (Soft-CHV, Jaccard, Dice, Set Coverage)
for 4 algorithms x 4 models x 4 datasets and produces:

  1) Radar chart              — aggregated rank scores per algorithm
  2) Dominance heatmap (CV)   — pairwise C(A,B) per dataset x classifier
  3) Dominance heatmap (ext)  — pairwise C(A,B) for algorithms with external results
  4) Sensitivity heatmap      — composite scores across weight scenarios

CV algorithms:
  - NSGA2-Std
  - NSGA2-CH
  - NSGA2-CHS
  - HPE-NSGA2-CHS

External validation:
  - NSGA2-Std
  - NSGA2-CH
  - NSGA2-CHS

HPE is not included in external validation because external validation
was not performed for the HPE experiments.

Usage:
  cd work/
  python3 ../py/plots/article_plots.py
"""

import os, sys
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
from saved_solutions.run_fold_jaccard import compute_jaccard_from_lists
from util.list_math import dice
from util.cross_hypervolume.cross_hypervolume import cross_hypervolume
from util.hyperbox.hyperbox import ConcreteHyperbox0B


OUTPUT_DIR = os.path.join(os.getcwd(), "article_plots")

DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]

DATASET_LABELS = {
    "brca": "TCGA-BRCA",
    "luad_lusc": "TCGA-LU",
    "tcga_kir": "TCGA-KI3",
    "tcga_ov": "TCGA-OV",
}


MODELS_MAP = {
    "naive_bayes": "NB_bal_acc_leanness",
    "svm": "leanness_svm_bal_acc",
    "RF": "RF_bal_acc_leanness",
    "logistic": "leanness_logit100_bal_acc",
}

MODEL_LABELS = {
    "naive_bayes": "NB",
    "svm": "SVM",
    "RF": "RF",
    "logistic": "LR",
}

MODEL_ORDER = [
    "naive_bayes",
    "svm",
    "RF",
    "logistic",
]


# ---------------------------------------------------------------------------
# Algorithms
# ---------------------------------------------------------------------------

ALGOS_CV = [
    "nsga2",
    "nsga2_ch",
    "nsga2_chs",
    "hpe_nsga2_chs",
]

ALGOS_EXT = [
    "nsga2",
    "nsga2_ch",
    "nsga2_chs",
]

ALGO_LABELS = {
    "nsga2": "NSGA2-Std",
    "nsga2_ch": "NSGA2-CH",
    "nsga2_chs": "NSGA2-CHS",
    "hpe_nsga2_chs": "HPE-NSGA2-CHS",
}

ALGO_SHORT = ALGO_LABELS.copy()

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


SCENARIOS = {
    "Equilibrado": [
        0.25,
        0.25,
        0.25,
        0.25,
    ],
    "Rendimiento": [
        0.50,
        0.05,
        0.15,
        0.30,
    ],
    "Descubrimiento": [
        0.35,
        0.25,
        0.15,
        0.25,
    ],
    "Reproducibilidad": [
        0.35,
        0.10,
        0.35,
        0.20,
    ],
}


EXT_DATASET_MAP = {
    "brca": ("brca", "swedish"),
    "luad_lusc": ("luad_lusc", "cptac3_sub_uq4"),
    "tcga_kir": ("tcga_kir3", "kid_gse152938d"),
    "tcga_ov": ("tcga_ov", "ext_ov2"),
}


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def get_obj_dir(dataset: str, model: str) -> str:
    return MODELS_MAP.get(model, "")


def big_params(model: str) -> dict:
    is_log = model == "logistic"

    return {
        "pop": 200 if is_log else 500,
        "evals": 200000 if is_log else 500000,
        "gen": 1000,
        "inner_folds": 3,
        "outer_folds": 5,
    }


def ext_params(model: str) -> dict:
    is_log = model == "logistic"

    return {
        "pop": 200 if is_log else 500,
        "evals": 200000 if is_log else 500000,
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

    if algo in ALGOS_CV:
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


def resolve_ext_and_build(
    dataset: str,
    model: str,
    algo: str,
) -> str:

    # HPE has no external validation.
    if algo not in ALGOS_EXT:
        return ""

    mapped = EXT_DATASET_MAP.get(dataset)

    if mapped is None:
        return ""

    ext_ds_dir, ext_ds_name = mapped

    p = ext_params(model)

    obj_dir = get_obj_dir(
        ext_ds_dir,
        model,
    )

    if not obj_dir:
        return ""

    algo_dir = get_expected_nsga_name(
        algo,
        p["pop"],
        p["gen"],
        p["inner_folds"],
    )

    if not algo_dir:
        return ""

    return os.path.join(
        os.getcwd(),
        ext_ds_dir,
        "mrna",
        obj_dir,
        "external_validation",
        ext_ds_name,
        algo_dir,
    )


# ---------------------------------------------------------------------------
# Data loading — CV
# ---------------------------------------------------------------------------

def compute_c_matrix(
    dataset: str,
    model: str,
) -> np.ndarray:

    n_algo = len(ALGOS_CV)

    mat = np.full(
        (n_algo, n_algo),
        np.nan,
    )

    paths = {
        algo: resolve_and_build(
            dataset,
            model,
            algo,
        )
        for algo in ALGOS_CV
    }

    data = {}

    for algo in ALGOS_CV:

        path = paths[algo]

        if not os.path.isdir(path):
            continue

        exp = get_data_from_exp(path)

        if exp is None:
            continue

        folds = exp.get("folds", {})

        if not folds:
            continue

        xs = []
        ys = []

        for fold in folds.values():
            xs.extend(fold["x"])
            ys.extend(fold["y"])

        if xs and ys:
            data[algo] = (
                np.array(xs),
                np.array(ys),
            )

    for i, algo_a in enumerate(ALGOS_CV):

        for j, algo_b in enumerate(ALGOS_CV):

            if i == j:
                continue

            if algo_a not in data or algo_b not in data:
                continue

            x_a, y_a = data[algo_a]
            x_b, y_b = data[algo_b]

            c_val = calculate_c_metric(
                x_a,
                y_a,
                x_b,
                y_b,
            )

            if not np.isnan(c_val):
                mat[i, j] = c_val

    return mat


def load_all_metrics() -> dict:

    result = {}

    for ds in DATASETS:

        result[ds] = {}

        for mod in MODELS_MAP:

            result[ds][mod] = {}

            c_mat = compute_c_matrix(
                ds,
                mod,
            )

            for ai, algo in enumerate(ALGOS_CV):

                path = resolve_and_build(
                    ds,
                    mod,
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

                dice_val = metrics.get(
                    "dice_m",
                    np.nan,
                )

                c_out_vals = [
                    c_mat[ai, j]
                    for j in range(len(ALGOS_CV))
                    if j != ai
                    and not np.isnan(c_mat[ai, j])
                ]

                c_in_vals = [
                    c_mat[j, ai]
                    for j in range(len(ALGOS_CV))
                    if j != ai
                    and not np.isnan(c_mat[j, ai])
                ]

                c_out = (
                    float(np.mean(c_out_vals))
                    if c_out_vals
                    else np.nan
                )

                c_in = (
                    float(np.mean(c_in_vals))
                    if c_in_vals
                    else np.nan
                )

                c_net = (
                    c_out - c_in
                    if not np.isnan(c_out)
                    and not np.isnan(c_in)
                    else np.nan
                )

                result[ds][mod][algo] = {
                    "schv": schv,
                    "jaccard": jaccard_raw,
                    "j_div": (
                        1.0 - jaccard_raw
                        if not np.isnan(jaccard_raw)
                        else np.nan
                    ),
                    "dice": dice_val,
                    "c_out": c_out,
                    "c_in": c_in,
                    "c_net": c_net,
                }

    return result


# ---------------------------------------------------------------------------
# Data loading — External validation
# ---------------------------------------------------------------------------

def load_ext_data(exp_path: str):

    target_dir = os.path.join(
        exp_path,
        "hofs",
        "Pareto",
    )

    if not os.path.exists(target_dir):
        return None

    feat_csv = os.path.join(
        target_dir,
        "solution_features.csv",
    )

    fit_csv = os.path.join(
        target_dir,
        "solution_fitnesses.csv",
    )

    if (
        not os.path.exists(feat_csv)
        or not os.path.exists(fit_csv)
    ):
        return None

    try:
        df_feat = pd.read_csv(feat_csv)
        df_fit = pd.read_csv(fit_csv)
    except Exception:
        return None

    if df_feat.empty or df_fit.empty:
        return None

    test_acc_col = next(
        (
            c for c in df_fit.columns
            if "test_" in c
            and "leanness" not in c
            and "class" not in c
        ),
        None,
    )

    lean_col = next(
        (
            c for c in df_fit.columns
            if "leanness" in c
            and "soft" not in c
        ),
        None,
    )

    if (
        test_acc_col is None
        or lean_col is None
    ):
        return None

    x = df_feat.sum(
        axis=1
    ).values

    y = df_fit[
        test_acc_col
    ].values

    s_idx = np.argsort(x)

    return (
        x[s_idx],
        y[s_idx],
    )


def compute_ext_c_matrix(
    dataset: str,
    model: str,
) -> np.ndarray:

    n_algo = len(ALGOS_EXT)

    mat = np.full(
        (n_algo, n_algo),
        np.nan,
    )

    paths = {
        algo: resolve_ext_and_build(
            dataset,
            model,
            algo,
        )
        for algo in ALGOS_EXT
    }

    data = {}

    for algo in ALGOS_EXT:

        path = paths[algo]

        if not os.path.isdir(path):
            continue

        values = load_ext_data(path)

        if values is None:
            continue

        data[algo] = values

    for i, algo_a in enumerate(ALGOS_EXT):

        for j, algo_b in enumerate(ALGOS_EXT):

            if i == j:
                continue

            if algo_a not in data or algo_b not in data:
                continue

            x_a, y_a = data[algo_a]
            x_b, y_b = data[algo_b]

            c_val = calculate_c_metric(
                x_a,
                y_a,
                x_b,
                y_b,
            )

            if not np.isnan(c_val):
                mat[i, j] = c_val

    return mat


# ---------------------------------------------------------------------------
# Data loading — External metrics
# ---------------------------------------------------------------------------

def load_ext_algo_metrics(exp_path):

    target_dir = os.path.join(
        exp_path,
        "hofs",
        "Pareto",
    )

    if not os.path.exists(target_dir):
        return None

    feat_csv = os.path.join(
        target_dir,
        "solution_features.csv",
    )

    fit_csv = os.path.join(
        target_dir,
        "solution_fitnesses.csv",
    )

    if (
        not os.path.exists(feat_csv)
        or not os.path.exists(fit_csv)
    ):
        return None

    try:
        df_feat = pd.read_csv(feat_csv)
        df_fit = pd.read_csv(fit_csv)
    except Exception:
        return None

    if df_feat.empty or df_fit.empty:
        return None

    feature_names = df_feat.columns.tolist()

    gene_lists = [
        [
            name
            for name, val in zip(
                feature_names,
                row,
            )
            if val == 1
        ]
        for _, row in df_feat.iterrows()
    ]

    jaccard_val = compute_jaccard_from_lists(
        gene_lists
    )

    n_sol = len(df_feat)

    if n_sol > 1:

        dice_sum = 0.0
        n_pairs = 0

        for r1 in range(n_sol):

            for r2 in range(
                r1 + 1,
                n_sol,
            ):

                dice_sum += dice(
                    df_feat.iloc[r1].tolist(),
                    df_feat.iloc[r2].tolist(),
                )

                n_pairs += 1

        dice_val = dice_sum / n_pairs

    else:
        dice_val = 1.0

    train_acc_col = next(
        (
            c for c in df_fit.columns
            if "internal_" in c
            and "leanness" not in c
            and "class" not in c
        ),
        None,
    )

    test_acc_col = next(
        (
            c for c in df_fit.columns
            if "test_" in c
            and "leanness" not in c
            and "class" not in c
        ),
        None,
    )

    lean_col = next(
        (
            c for c in df_fit.columns
            if "leanness" in c
            and "soft" not in c
        ),
        None,
    )

    schv = np.nan

    if (
        train_acc_col
        and test_acc_col
        and lean_col
    ):

        tr_boxes = [
            ConcreteHyperbox0B.create_by_b_vals(
                (
                    r[train_acc_col],
                    1.0 / (
                        1.0
                        + np.sqrt(
                            max(
                                0,
                                round(
                                    1.0
                                    / r[lean_col]
                                    - 1.0
                                ),
                            )
                        )
                    ),
                )
            )
            for _, r in df_fit.iterrows()
        ]

        te_boxes = [
            ConcreteHyperbox0B.create_by_b_vals(
                (
                    r[test_acc_col],
                    1.0 / (
                        1.0
                        + np.sqrt(
                            max(
                                0,
                                round(
                                    1.0
                                    / r[lean_col]
                                    - 1.0
                                ),
                            )
                        )
                    ),
                )
            )
            for _, r in df_fit.iterrows()
        ]

        schv = cross_hypervolume(
            tr_boxes,
            te_boxes,
        )

    return {
        "schv_m": schv,
        "var_m": jaccard_val,
        "dice_m": dice_val,
    }


def load_ext_all_metrics() -> dict:

    result = {}

    for ds in DATASETS:

        result[ds] = {}

        for mod in MODELS_MAP:

            result[ds][mod] = {}

            c_mat = compute_ext_c_matrix(
                ds,
                mod,
            )

            for ai, algo in enumerate(ALGOS_EXT):

                path = resolve_ext_and_build(
                    ds,
                    mod,
                    algo,
                )

                if (
                    not path
                    or not os.path.isdir(path)
                ):
                    continue

                em = load_ext_algo_metrics(
                    path
                )

                if em is None:
                    continue

                jaccard_raw = em.get(
                    "var_m",
                    np.nan,
                )

                schv = em.get(
                    "schv_m",
                    np.nan,
                )

                dice_val = em.get(
                    "dice_m",
                    np.nan,
                )

                c_out_vals = [
                    c_mat[ai, j]
                    for j in range(len(ALGOS_EXT))
                    if j != ai
                    and not np.isnan(c_mat[ai, j])
                ]

                c_in_vals = [
                    c_mat[j, ai]
                    for j in range(len(ALGOS_EXT))
                    if j != ai
                    and not np.isnan(c_mat[j, ai])
                ]

                c_out = (
                    float(np.mean(c_out_vals))
                    if c_out_vals
                    else np.nan
                )

                c_in = (
                    float(np.mean(c_in_vals))
                    if c_in_vals
                    else np.nan
                )

                c_net = (
                    c_out - c_in
                    if not np.isnan(c_out)
                    and not np.isnan(c_in)
                    else np.nan
                )

                result[ds][mod][algo] = {
                    "schv": schv,
                    "jaccard": jaccard_raw,
                    "j_div": (
                        1.0 - jaccard_raw
                        if not np.isnan(jaccard_raw)
                        else np.nan
                    ),
                    "dice": dice_val,
                    "c_out": c_out,
                    "c_in": c_in,
                    "c_net": c_net,
                }

    return result


# ---------------------------------------------------------------------------
# Dominance grid data
# ---------------------------------------------------------------------------

def compute_dominance_grid(mode: str):

    algos = (
        ALGOS_CV
        if mode == "cv"
        else ALGOS_EXT
    )

    n_algo = len(algos)
    n_ds = len(DATASETS)
    n_mod = len(MODEL_ORDER)

    grid = np.full(
        (
            n_ds,
            n_mod,
            n_algo,
            n_algo,
        ),
        np.nan,
    )

    for di, ds in enumerate(DATASETS):

        for mj, mod in enumerate(MODEL_ORDER):

            if mode == "cv":
                grid[di, mj] = compute_c_matrix(
                    ds,
                    mod,
                )
            else:
                grid[di, mj] = compute_ext_c_matrix(
                    ds,
                    mod,
                )

    avg_grid = np.full(
        (
            n_ds,
            n_algo,
            n_algo,
        ),
        np.nan,
    )

    for di in range(n_ds):
        avg_grid[di] = np.nanmean(
            grid[di],
            axis=0,
        )

    return grid, avg_grid


# ---------------------------------------------------------------------------
# Rank normalization
# ---------------------------------------------------------------------------

def rank_normalize(values: list) -> np.ndarray:

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

    valid_vals = arr[
        valid_mask
    ]

    order = np.argsort(
        valid_vals
    )[::-1]

    ranks = np.empty_like(
        valid_vals
    )

    ranks[order] = np.arange(
        1,
        len(valid_vals) + 1,
    )

    scores[valid_mask] = (
        len(valid_vals) - ranks
    ) / max(
        1,
        len(valid_vals) - 1,
    )

    return scores


def compute_rank_scores(
    raw: dict,
    algos: list,
) -> dict:

    result = {}

    for ds in DATASETS:

        result[ds] = {}

        for mod in MODELS_MAP:

            result[ds][mod] = {}

            for met in METRICS:

                vals = []

                for algo in algos:

                    entry = raw[
                        ds
                    ][
                        mod
                    ].get(algo)

                    if entry is None:
                        vals.append(np.nan)
                    else:
                        vals.append(
                            entry.get(
                                met,
                                np.nan,
                            )
                        )

                rs = rank_normalize(vals)

                for ai, algo in enumerate(algos):

                    if algo not in result[ds][mod]:
                        result[ds][mod][algo] = {}

                    result[ds][mod][algo][
                        met + "_rank"
                    ] = rs[ai]

    return result


def aggregate_ranks(
    ranked: dict,
    algos: list,
) -> np.ndarray:

    n_algo = len(algos)

    per_dataset = np.full(
        (
            len(DATASETS),
            n_algo,
            len(METRICS),
        ),
        np.nan,
    )

    for di, ds in enumerate(DATASETS):

        for ai, algo in enumerate(algos):

            for mi, met in enumerate(METRICS):

                vals = []

                for mod in MODELS_MAP:

                    v = ranked[
                        ds
                    ][
                        mod
                    ].get(
                        algo,
                        {},
                    ).get(
                        met + "_rank",
                        np.nan,
                    )

                    if not np.isnan(v):
                        vals.append(v)

                if vals:
                    per_dataset[
                        di,
                        ai,
                        mi,
                    ] = np.mean(vals)

    return np.nanmean(
        per_dataset,
        axis=0,
    )


# ---------------------------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------------------------

def sensitivity_analysis(
    aggregated: np.ndarray,
    algos: list,
) -> pd.DataFrame:

    rows = []

    for scenario_name, weights in SCENARIOS.items():

        w = np.array(weights)

        scores = aggregated @ w

        for ai, algo in enumerate(algos):

            rows.append({
                "Algorithm": ALGO_SHORT[algo],
                "Scenario": scenario_name,
                "CompositeScore": scores[ai],
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------

RADAR_COLORS = {
    "nsga2": "#377EB8",
    "nsga2_ch": "#4DAF4A",
    "nsga2_chs": "#984EA3",
    "hpe_nsga2_chs": "#E41A1C",
}


def plot_radar(
    aggregated: np.ndarray,
    title: str,
    filename: str,
    algos: list,
):

    n_metrics = len(METRICS)

    angles = np.linspace(
        0,
        2 * np.pi,
        n_metrics,
        endpoint=False,
    ).tolist()

    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=(7, 7),
        subplot_kw={"polar": True},
    )

    for ai, algo in enumerate(algos):

        vals = aggregated[
            ai
        ].tolist()

        vals += vals[:1]

        ax.plot(
            angles,
            vals,
            "o-",
            color=RADAR_COLORS[algo],
            linewidth=2,
            label=ALGO_SHORT[algo],
        )

        ax.fill(
            angles,
            vals,
            alpha=0.12,
            color=RADAR_COLORS[algo],
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

    ax.set_yticklabels(
        [
            "0.2",
            "0.4",
            "0.6",
            "0.8",
            "1.0",
        ],
        fontsize=8,
    )

    ax.set_title(
        title,
        fontsize=13,
        fontweight="bold",
        pad=25,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.35, 1.12),
        fontsize=9,
        framealpha=0.9,
    )

    plt.subplots_adjust(
        right=0.75
    )

    path = os.path.join(
        OUTPUT_DIR,
        filename,
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"  [SAVED] {path}")


def _save_single_dominance(
    mat,
    out_dir,
    fname,
    algos,
    vmin=0.0,
    vmax=1.0,
):

    os.makedirs(
        out_dir,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(4, 3.5)
    )

    mat = mat.copy()

    np.fill_diagonal(
        mat,
        np.nan,
    )

    mask = np.isnan(mat)

    algo_names = [
        ALGO_SHORT[a]
        for a in algos
    ]

    annot = np.array([
        [
            ""
            if np.isnan(v)
            else f"{v:.2f}"
            for v in row
        ]
        for row in mat
    ])

    sns.heatmap(
        mat,
        annot=annot,
        fmt="",
        cmap="RdYlGn",
        xticklabels=algo_names,
        yticklabels=algo_names,
        ax=ax,
        linewidths=0.8,
        linecolor="gray",
        vmin=vmin,
        vmax=vmax,
        mask=mask,
        cbar_kws={
            "label": "C(A,B)"
        },
    )

    ax.tick_params(
        labelsize=7
    )

    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation=90,
        fontsize=7,
    )

    ax.set_yticklabels(
        ax.get_yticklabels(),
        rotation=0,
        fontsize=7,
    )

    plt.tight_layout()

    path = os.path.join(
        out_dir,
        fname,
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"  [SAVED] {path}")


def plot_dominance_individuals():

    for mode_label, mode_key in [
        ("cv", "cv"),
        ("external", "external"),
    ]:

        print(
            f"  Computing {mode_label} dominance grid..."
        )

        grid, avg_grid = compute_dominance_grid(
            mode_key
        )

        algos = (
            ALGOS_CV
            if mode_key == "cv"
            else ALGOS_EXT
        )

        base_dir = os.path.join(
            OUTPUT_DIR,
            "dominance",
            mode_label,
        )

        for di, ds in enumerate(DATASETS):

            ds_dir = os.path.join(
                base_dir,
                DATASET_LABELS.get(
                    ds,
                    ds,
                ),
            )

            for mj, mod in enumerate(
                MODEL_ORDER
            ):

                mat = grid[
                    di,
                    mj,
                ]

                if np.all(
                    np.isnan(mat)
                ):
                    continue

                _save_single_dominance(
                    mat,
                    ds_dir,
                    f"{MODEL_LABELS[mod]}.pdf",
                    algos,
                )

            mat_avg = avg_grid[
                di
            ]

            if not np.all(
                np.isnan(mat_avg)
            ):

                _save_single_dominance(
                    mat_avg,
                    ds_dir,
                    "Avg.pdf",
                    algos,
                )


def plot_sensitivity_heatmap(
    sens_df: pd.DataFrame,
    algos: list,
    filename: str,
):

    pivot = sens_df.pivot_table(
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
        ALGO_SHORT[a]
        for a in algos
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
        filename,
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"  [SAVED] {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    print(
        f"\n{'=' * 65}"
    )

    print(
        " ARTICLE PLOTS — Big CV Analysis"
    )

    print(
        f"  Output: {OUTPUT_DIR}"
    )

    print(
        f"{'=' * 65}\n"
    )

    print(
        "[1/6] Loading CV metrics..."
    )

    raw_cv = load_all_metrics()

    print(
        "[2/6] Loading external metrics..."
    )

    raw_ext = load_ext_all_metrics()

    print(
        "[3/6] Computing rank-based normalization (CV)..."
    )

    ranked_cv = compute_rank_scores(
        raw_cv,
        ALGOS_CV,
    )

    print(
        "[4/6] Aggregating across classifiers and datasets (CV)..."
    )

    aggregated_cv = aggregate_ranks(
        ranked_cv,
        ALGOS_CV,
    )

    print(
        "  CV Aggregated scores (algo × metric):"
    )

    print(
        f"  {'Algo':>20s}"
        + "".join(
            f"{lbl:>15s}"
            for lbl in METRIC_LABELS
        )
    )

    for ai, algo in enumerate(
        ALGOS_CV
    ):

        row = (
            f"  {ALGO_SHORT[algo]:>20s}"
        )

        for mi in range(
            len(METRICS)
        ):

            row += (
                f"{aggregated_cv[ai, mi]:>15.4f}"
            )

        print(row)

    print(
        "  Computing rank-based normalization (external)..."
    )

    ranked_ext = compute_rank_scores(
        raw_ext,
        ALGOS_EXT,
    )

    print(
        "  Aggregating across classifiers and datasets (external)..."
    )

    aggregated_ext = aggregate_ranks(
        ranked_ext,
        ALGOS_EXT,
    )

    print(
        "  External Aggregated scores (algo × metric):"
    )

    print(
        f"  {'Algo':>20s}"
        + "".join(
            f"{lbl:>15s}"
            for lbl in METRIC_LABELS
        )
    )

    for ai, algo in enumerate(
        ALGOS_EXT
    ):

        row = (
            f"  {ALGO_SHORT[algo]:>20s}"
        )

        for mi in range(
            len(METRICS)
        ):

            row += (
                f"{aggregated_ext[ai, mi]:>15.4f}"
            )

        print(row)

    print(
        "[5/6] Generating PDF figures..."
    )

    sens_df = sensitivity_analysis(
        aggregated_cv,
        ALGOS_CV,
    )

    plot_radar(
        aggregated_cv,
        "CV — Aggregated Rank Scores",
        "radar_profiles_cv.pdf",
        ALGOS_CV,
    )

    plot_radar(
        aggregated_ext,
        "External — Aggregated Rank Scores",
        "radar_profiles_external.pdf",
        ALGOS_EXT,
    )

    plot_dominance_individuals()

    plot_sensitivity_heatmap(
        sens_df,
        ALGOS_CV,
        "sensitivity_heatmap.pdf",
    )

    print(
        f"\nDone. All outputs in {OUTPUT_DIR}\n"
    )


if __name__ == "__main__":
    main()