"""Generador de mapas de calor de cobertura de conjuntos (métrica C) para MONOMER.

Computes C(A,B) = proportion of solutions in B dominated by A.
Supports:
  - raw: direct C(A,B) values
  - abs: C(A,B) - C(B,A)
  - pct: relative percentage difference

Plot modes:
  - matrix: algorithm x algorithm matrix
  - suite: dataset x model for one algorithm pair
  - biggrid: dataset/model grid with one algorithm matrix per cell
  - pivotgrid: algorithm-pair grid with dataset/model submatrices
  - metricgrid: dataset/model heatmaps for each algorithm

Run from work/ directory.
"""

import os
import sys
import argparse
import numpy as np

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, '..', '..'))
sys.path.append(os.path.join(_PROJECT_ROOT, 'py'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from plots.plot_labels import NSGA2_LAB, NSGA2_CH_LAB, NSGA2_CHS_LAB, HPE_NSGA2_CHS_LAB
from scratch.plot_interactive import calculate_c_metric, get_data_from_exp, get_expected_nsga_name


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORK_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(WORK_DIR, "tuning_reports", "Set_Coverage")

DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]

DATASET_LABELS = {
    "brca": "BRCA",
    "luad_lusc": "LUAD-LUSC",
    "tcga_kir": "KIR",
    "tcga_ov": "OV",
}

MODEL_LABELS = {
    "naive_bayes": "Naive Bayes",
    "svm": "SVM",
    "RF": "Random Forest",
    "logistic": "Regresión Logística",
}


MODELS_MAP = {
    "naive_bayes": "NB_bal_acc_leanness",
    "svm": "leanness_svm_bal_acc",
    "RF": "RF_bal_acc_leanness",
    "logistic": "leanness_logit100_bal_acc",
}

ALGOS = ["nsga2", "nsga2_ch", "nsga2_chs", "hpe_nsga2_chs"]

ALGO_LABELS = {
    "nsga2": "NSGA-II",
    "nsga2_ch": "NSGA-II + CH",
    "nsga2_chs": "NSGA-II + CHS",
    "hpe_nsga2_chs": "HPE + NSGA-II + CHS",
}

DIFF_MODES = ("raw", "abs", "pct")

DIFF_SAT = {
    "raw": (0.0, 1.0),
    "abs": (-0.3, 0.3),
    "pct": (-50.0, 50.0),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_obj_dir(dataset: str, model: str) -> str:
    return MODELS_MAP.get(model, "")


def cmatrix_to_diff(mat: np.ndarray, mode: str) -> np.ndarray:
    """Transform C(A,B) matrix into raw, absolute difference or percentage difference."""
    if mode == "raw":
        return mat.copy()

    n = mat.shape[0]
    out = np.full_like(mat, np.nan)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            cij = mat[i, j]
            cji = mat[j, i]

            if np.isnan(cij) or np.isnan(cji):
                continue

            if mode == "abs":
                out[i, j] = cij - cji
            elif mode == "pct":
                denom = max(cij, cji, 1e-8)
                out[i, j] = (cij - cji) / denom * 100.0

    return out


# ---------------------------------------------------------------------------
# Experiment parameters
# ---------------------------------------------------------------------------
def big_params(model: str) -> dict:
    is_log = model == "logistic"
    return {"pop": 200 if is_log else 500, "gen": 1000, "inner_folds": 3, "outer_folds": 5}


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
def resolve_algo_dir(algo: str, pop: int, gen: int, inner_folds: int) -> str:
    return get_expected_nsga_name(base_algo=algo, pop=pop, gen=gen, inner_folds=inner_folds)


def build_exp_path(dataset: str, model: str, algo: str, pop: int, gen: int, inner_folds: int, outer_folds: int) -> str:
    obj_dir = get_obj_dir(dataset, model)

    if not obj_dir:
        return ""

    algo_dir = resolve_algo_dir(algo=algo, pop=pop, gen=gen, inner_folds=inner_folds)

    if not algo_dir:
        return ""

    return os.path.join(WORK_DIR, dataset, "mrna", obj_dir, f"{outer_folds}_folds", algo_dir)


def resolve_and_build(dataset: str, model: str, algo: str, setup: str) -> str:
    if setup == "small":
        return build_exp_path(dataset, model, algo, pop=52, gen=100, inner_folds=2, outer_folds=2)

    p = big_params(model)

    return build_exp_path(dataset, model, algo, pop=p["pop"], gen=p["gen"], inner_folds=p["inner_folds"], outer_folds=p["outer_folds"])

# ---------------------------------------------------------------------------
# C-metric
# ---------------------------------------------------------------------------

def compute_cmetric_global(exp_path_a: str, exp_path_b: str) -> float:
    """Compute C(A,B) using the solutions from all folds."""
    data_a = get_data_from_exp(exp_path_a)
    data_b = get_data_from_exp(exp_path_b)

    if data_a is None or data_b is None:
        return float("nan")

    folds_a = data_a.get("folds", {})
    folds_b = data_b.get("folds", {})

    if not folds_a or not folds_b:
        return float("nan")

    xs_a, ys_a = [], []
    xs_b, ys_b = [], []

    for fold in folds_a.values():
        xs_a.extend(fold["x"])
        ys_a.extend(fold["y"])

    for fold in folds_b.values():
        xs_b.extend(fold["x"])
        ys_b.extend(fold["y"])

    if not xs_a or not xs_b:
        return float("nan")

    return calculate_c_metric(np.array(xs_a), np.array(ys_a), np.array(xs_b), np.array(ys_b))


def compute_4x4_matrix(dataset: str, model: str, setup: str) -> np.ndarray:
    """Return the algorithm x algorithm C-matrix for one dataset and model."""
    n = len(ALGOS)
    mat = np.full((n, n), np.nan)

    paths = {algo: resolve_and_build(dataset, model, algo, setup) for algo in ALGOS}

    for i, algo_a in enumerate(ALGOS):
        for j, algo_b in enumerate(ALGOS):
            if i == j:
                continue

            path_a = paths[algo_a]
            path_b = paths[algo_b]

            if not os.path.isdir(path_a) or not os.path.isdir(path_b):
                continue

            value = compute_cmetric_global(path_a, path_b)

            if not np.isnan(value):
                mat[i, j] = value

    return mat


def compute_algo_pair_matrix(algo_a: str, algo_b: str, setup: str) -> np.ndarray:
    """Return the dataset x model C-matrix for one fixed algorithm pair."""
    datasets = [d + "_mini" if setup == "small" else d for d in DATASETS]
    models = list(MODELS_MAP.keys())

    mat = np.full((len(datasets), len(models)), np.nan)

    for i, dataset in enumerate(datasets):
        for j, model in enumerate(models):
            path_a = resolve_and_build(dataset, model, algo_a, setup)
            path_b = resolve_and_build(dataset, model, algo_b, setup)

            if not os.path.isdir(path_a) or not os.path.isdir(path_b):
                continue

            value = compute_cmetric_global(path_a, path_b)

            if not np.isnan(value):
                mat[i, j] = value

    return mat


# ---------------------------------------------------------------------------
# Matrix heatmap
# ---------------------------------------------------------------------------

def _plot_matrix_heatmap(matrix, algo_labels, title, filename, diff_mode="raw"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    n = len(algo_labels)
    mask = np.eye(n, dtype=bool)
    vmin, vmax = DIFF_SAT[diff_mode]
    fmt = ".1f" if diff_mode == "pct" else ".2f"

    cbar_label = {
        "raw": "C(A, B)",
        "abs": "C(A,B) − C(B,A)",
        "pct": "Diferencia porcentual (A frente a B)",
    }[diff_mode]

    annot = np.empty_like(matrix, dtype=object)

    for i in range(n):
        for j in range(n):
            value = matrix[i, j]

            if np.isnan(value):
                annot[i, j] = "X"
            elif diff_mode == "pct":
                annot[i, j] = f"{value:.1f}"
            else:
                annot[i, j] = f"{value:.2f}"

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(matrix, mask=mask, annot=annot, fmt="", xticklabels=algo_labels, yticklabels=algo_labels, cmap="RdYlGn", vmin=vmin, vmax=vmax, center=0.0 if diff_mode != "raw" else None, cbar_kws={"label": cbar_label}, ax=ax, linewidths=1, linecolor="gray", square=True)

    ax.set_xlabel("Algoritmo B", fontsize=12)
    ax.set_ylabel("Algoritmo A", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [SAVED] {os.path.join(OUTPUT_DIR, filename)}")


def build_matrix(args):
    datasets = [args.dataset] if args.dataset and args.model else [d + "_mini" if args.setup == "small" else d for d in DATASETS]
    models = [args.model] if args.dataset and args.model else list(MODELS_MAP.keys())

    agg = []
    final_mat = np.full((len(ALGOS), len(ALGOS)), np.nan)

    for dataset in datasets:
        for model in models:
            mat = compute_4x4_matrix(dataset, model, args.setup)

            if args.dataset and args.model:
                final_mat = mat
            else:
                for i in range(len(ALGOS)):
                    for j in range(len(ALGOS)):
                        if i != j and not np.isnan(mat[i, j]):
                            agg.append((i, j, mat[i, j]))

    if not (args.dataset and args.model) and agg:
        final_mat = np.full((len(ALGOS), len(ALGOS)), np.nan)

        for i in range(len(ALGOS)):
            for j in range(len(ALGOS)):
                if i == j:
                    continue

                values = [value for vi, vj, value in agg if vi == i and vj == j]

                if values:
                    final_mat[i, j] = float(np.mean(values))

    labels = [ALGO_LABELS[algo] for algo in ALGOS]
    diff_mode = args.diff_mode
    final_diff = cmatrix_to_diff(final_mat, diff_mode)

    suffix = {"raw": "", "abs": "_absdiff", "pct": "_pctdiff"}[diff_mode]
    mode_tag = {"raw": "", "abs": " [diferencia absoluta]", "pct": " [diferencia porcentual]"}[diff_mode]

    if args.dataset and args.model:
        title = f"Cobertura de conjuntos 4×4 — {args.dataset} / {args.model} ({args.setup}){mode_tag}"
        filename = f"matrix_{args.setup}_{args.dataset}_{args.model}{suffix}.png"
    else:
        title = f"Cobertura de conjuntos 4×4 — Media global ({args.setup}){mode_tag}"
        filename = f"matrix_{args.setup}_global{suffix}.png"

    _plot_matrix_heatmap(final_diff, labels, title, filename, diff_mode=diff_mode)


# ---------------------------------------------------------------------------
# Suite heatmap
# ---------------------------------------------------------------------------

def _plot_suite_heatmap(grid, dataset_labels, model_labels, algo_a_label, algo_b_label, setup, filename, diff_mode="raw"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    vmin, vmax = DIFF_SAT[diff_mode]
    fmt = ".1f" if diff_mode == "pct" else ".2f"

    cbar_label = {
        "raw": f"C({algo_a_label}, {algo_b_label})",
        "abs": f"C({algo_a_label},{algo_b_label}) − C({algo_b_label},{algo_a_label})",
        "pct": f"Diferencia porcentual ({algo_a_label} frente a {algo_b_label})",
    }[diff_mode]

    fig, ax = plt.subplots(figsize=(10, 7))

    sns.heatmap(grid, annot=True, fmt=fmt, xticklabels=model_labels, yticklabels=dataset_labels, cmap="RdYlGn", vmin=vmin, vmax=vmax, center=0.0 if diff_mode != "raw" else None, cbar_kws={"label": cbar_label}, ax=ax, linewidths=1, linecolor="gray", square=True)

    ax.set_xlabel("Modelo / Clasificador", fontsize=12)
    ax.set_ylabel("Conjunto de datos", fontsize=12)

    mode_tag = {"raw": "", "abs": " [diferencia absoluta]", "pct": " [diferencia porcentual]"}[diff_mode]

    ax.set_title(f"Cobertura de conjuntos — C({algo_a_label}, {algo_b_label}) — {setup}{mode_tag}", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [SAVED] {os.path.join(OUTPUT_DIR, filename)}")


def build_suite(args):
    if not args.algo_A or not args.algo_B:
        print("Error: --algo_A and --algo_B required for --plot_type suite")
        return

    datasets = [args.dataset] if args.dataset else [d + "_mini" if args.setup == "small" else d for d in DATASETS]
    models = [args.model] if args.model else list(MODELS_MAP.keys())

    grid = np.full((len(datasets), len(models)), np.nan)

    for i, dataset in enumerate(datasets):
        for j, model in enumerate(models):
            path_a = resolve_and_build(dataset, model, args.algo_A, args.setup)
            path_b = resolve_and_build(dataset, model, args.algo_B, args.setup)

            if os.path.isdir(path_a) and os.path.isdir(path_b):
                value = compute_cmetric_global(path_a, path_b)

                if not np.isnan(value):
                    grid[i, j] = value

    dataset_labels = [DATASET_LABELS.get(d.replace("_mini", ""), d.replace("_mini", "")) + (" (mini)" if d.endswith("_mini") else "") for d in datasets]
    model_labels = [MODEL_LABELS.get(model, model) for model in models]

    diff_mode = args.diff_mode
    suffix = {"raw": "", "abs": "_absdiff", "pct": "_pctdiff"}[diff_mode]

    filename = f"suite_{args.setup}_{args.algo_A}_vs_{args.algo_B}{suffix}.png"

    _plot_suite_heatmap(grid, dataset_labels, model_labels, args.algo_A, args.algo_B, args.setup, filename, diff_mode=diff_mode)


# ---------------------------------------------------------------------------
# Pivot grid
# ---------------------------------------------------------------------------

def build_pivot_grid(args):
    datasets = DATASETS
    models = list(MODELS_MAP.keys())

    n_algo = len(ALGOS)
    n_datasets = len(datasets)

    short_algo = [ALGO_LABELS[algo].replace("\n", " ") for algo in ALGOS]
    diff_mode = args.diff_mode

    vmin, vmax = DIFF_SAT[diff_mode]
    fmt = ".1f" if diff_mode == "pct" else ".2f"

    cbar_label = {
        "raw": "C(A, B)",
        "abs": "C(A,B) − C(B,A)",
        "pct": "Diferencia porcentual (A frente a B)",
    }[diff_mode]

    mats = {}

    for algo_a in ALGOS:
        for algo_b in ALGOS:
            if algo_a == algo_b:
                continue

            raw = compute_algo_pair_matrix(algo_a, algo_b, "big")

            if diff_mode == "raw":
                mats[(algo_a, algo_b)] = raw
                continue

            reverse = compute_algo_pair_matrix(algo_b, algo_a, "big")
            diff = np.full_like(raw, np.nan)

            for i in range(n_datasets):
                for j in range(len(models)):
                    cij = raw[i, j]
                    cji = reverse[i, j]

                    if np.isnan(cij) or np.isnan(cji):
                        continue

                    if diff_mode == "abs":
                        diff[i, j] = cij - cji
                    elif diff_mode == "pct":
                        denom = max(cij, cji, 1e-8)
                        diff[i, j] = (cij - cji) / denom * 100.0

            mats[(algo_a, algo_b)] = diff

    fig, axes = plt.subplots(n_algo, n_algo, figsize=(2.4 * n_algo + 1.5, 2.2 * n_algo + 2.0), squeeze=False)

    for i, algo_a in enumerate(ALGOS):
        for j, algo_b in enumerate(ALGOS):
            ax = axes[i, j]

            if i == j:
                ax.set_visible(False)
                continue

            mat = mats[(algo_a, algo_b)]

            annot = np.empty_like(mat, dtype=object)

            for ii in range(n_datasets):
                for jj in range(len(models)):
                    value = mat[ii, jj]
                    annot[ii, jj] = f"{value:{fmt}}" if not np.isnan(value) else ""

            sns.heatmap(mat, annot=annot, fmt="", xticklabels=[] if i < n_algo - 1 else models, yticklabels=[] if j > 0 else datasets, cmap="RdYlGn", vmin=vmin, vmax=vmax, center=0.0 if diff_mode != "raw" else None, cbar=False, ax=ax, linewidths=0.5, linecolor="gray", square=True)

            if j == (1 if i == 0 else 0):
                ax.set_ylabel(short_algo[i], fontsize=9, fontweight="bold")

            if i == (1 if j == 0 else 0):
                ax.set_title(short_algo[j], fontsize=9, fontweight="bold", pad=4)

    cbar_ax = fig.add_axes([0.92, 0.12, 0.015, 0.75])
    sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=plt.Normalize(vmin, vmax))
    sm.set_array([])
    fig.colorbar(sm, cax=cbar_ax, label=cbar_label)

    mode_tag = {"raw": "", "abs": " [diferencia absoluta]", "pct": " [diferencia porcentual]"}[diff_mode]

    fig.suptitle(f"Cobertura de conjuntos 4×4 por par de algoritmos{mode_tag}", fontsize=14, fontweight="bold", y=0.98)

    plt.tight_layout(rect=[0, 0, 0.90, 0.95])

    suffix = {"raw": "", "abs": "_absdiff", "pct": "_pctdiff"}[diff_mode]
    filename = f"pivotgrid_4x4_per_pair{suffix}.png"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [SAVED] {os.path.join(OUTPUT_DIR, filename)}")


# ---------------------------------------------------------------------------
# Big grid
# ---------------------------------------------------------------------------

def build_big_grid(args):
    datasets = DATASETS
    models = list(MODELS_MAP.keys())

    n_datasets = len(datasets)
    n_models = len(models)
    n_algo = len(ALGOS)

    algo_labels = [ALGO_LABELS[algo] for algo in ALGOS]
    diff_mode = args.diff_mode

    vmin, vmax = DIFF_SAT[diff_mode]
    fmt = ".1f" if diff_mode == "pct" else ".2f"

    cbar_label = {
        "raw": "C(A, B)",
        "abs": "C(A,B) − C(B,A)",
        "pct": "Diferencia porcentual (A frente a B)",
    }[diff_mode]

    mats = {}

    for dataset in datasets:
        for model in models:
            raw = compute_4x4_matrix(dataset, model, "big")
            mats[(dataset, model)] = cmatrix_to_diff(raw, diff_mode)

    fig, axes = plt.subplots(n_datasets, n_models, figsize=(3.2 * n_models + 1.5, 3.0 * n_datasets + 2.0), squeeze=False)

    for i, dataset in enumerate(datasets):
        for j, model in enumerate(models):
            ax = axes[i, j]
            mat = mats[(dataset, model)]
            mask = np.eye(n_algo, dtype=bool)

            annot = np.empty_like(mat, dtype=object)

            for ii in range(n_algo):
                for jj in range(n_algo):
                    value = mat[ii, jj]
                    annot[ii, jj] = f"{value:{fmt}}" if not np.isnan(value) else ""

            sns.heatmap(mat, mask=mask, annot=annot, fmt="", xticklabels=[] if i < n_datasets - 1 else algo_labels, yticklabels=[] if j > 0 else algo_labels, cmap="RdYlGn", vmin=vmin, vmax=vmax, center=0.0 if diff_mode != "raw" else None, cbar=False, ax=ax, linewidths=0.5, linecolor="gray", square=True)

            ax.set_title(f"{DATASET_LABELS.get(dataset, dataset)} / {MODEL_LABELS.get(model, model)}", fontsize=9, fontweight="bold", pad=2)

            if j == 0:
                ax.set_ylabel("Algoritmo A", fontsize=8)

            if i == n_datasets - 1:
                ax.set_xlabel("Algoritmo B", fontsize=8)

    cbar_ax = fig.add_axes([0.92, 0.12, 0.015, 0.75])
    sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=plt.Normalize(vmin, vmax))
    sm.set_array([])
    fig.colorbar(sm, cax=cbar_ax, label=cbar_label)

    mode_tag = {"raw": "", "abs": " [diferencia absoluta]", "pct": " [diferencia porcentual]"}[diff_mode]

    fig.suptitle(f"Cobertura de conjuntos 4×4{mode_tag}", fontsize=14, fontweight="bold", y=0.98)

    plt.tight_layout(rect=[0, 0, 0.90, 0.95])

    suffix = {"raw": "", "abs": "_absdiff", "pct": "_pctdiff"}[diff_mode]
    filename = f"biggrid_4x4_subplots{suffix}.png"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [SAVED] {os.path.join(OUTPUT_DIR, filename)}")


# ---------------------------------------------------------------------------
# Metric grid
# ---------------------------------------------------------------------------

METRIC_DEFS = {
    "chv": ("Hipervolumen cruzado", "chv_m"),
    "schv": ("Hipervolumen cruzado suavizado", "schv_m"),
    "jaccard": ("Estabilidad Jaccard", "var_m"),
    "dice": ("Coeficiente Dice", "dice_m"),
}

ALL_METRICS = list(METRIC_DEFS.keys())


def get_exp_metric(exp_path: str, metric_key: str) -> float:
    data = get_data_from_exp(exp_path)

    if data is None:
        return float("nan")

    return data.get("metrics", {}).get(metric_key, float("nan"))


def compute_algo_metric_4x4(algo: str, metric_key: str, setup: str) -> np.ndarray:
    datasets = [d + "_mini" if setup == "small" else d for d in DATASETS]
    models = list(MODELS_MAP.keys())

    mat = np.full((len(datasets), len(models)), np.nan)

    for i, dataset in enumerate(datasets):
        for j, model in enumerate(models):
            path = resolve_and_build(dataset, model, algo, setup)

            if not os.path.isdir(path):
                continue

            value = get_exp_metric(path, metric_key)

            if not np.isnan(value):
                mat[i, j] = value

    return mat


def _global_bounds(matrices):
    values = [value for matrix in matrices for row in matrix for value in row if not np.isnan(value)]

    if not values:
        return 0.0, 1.0

    vmin = min(values)
    vmax = max(values)

    if vmin == vmax:
        vmin -= 0.05
        vmax += 0.05

    return vmin, vmax


def build_metric_grid(args):
    datasets = DATASETS
    models = list(MODELS_MAP.keys())
    n_algo = len(ALGOS)

    selected = [args.metric] if args.metric else ALL_METRICS

    for metric in selected:
        label, metric_key = METRIC_DEFS[metric]

        algo_mats = {algo: compute_algo_metric_4x4(algo, metric_key, "big") for algo in ALGOS}

        fig, axes = plt.subplots(1, n_algo, figsize=(4.0 * n_algo, 3.5), squeeze=False)

        for j, algo in enumerate(ALGOS):
            ax = axes[0, j]
            mat = algo_mats[algo]

            annot = np.empty_like(mat, dtype=object)

            for i in range(len(datasets)):
                for k in range(len(models)):
                    value = mat[i, k]
                    annot[i, k] = f"{value:.3f}" if not np.isnan(value) else ""

            sns.heatmap(mat, annot=annot, fmt="", xticklabels=[] if j > 0 else models, yticklabels=datasets, cmap="RdYlGn", ax=ax, linewidths=0.5, linecolor="gray", square=True, cbar=False)

            ax.set_title(ALGO_LABELS[algo].replace("\n", " "), fontsize=10, fontweight="bold")

            if j == 0:
                ax.set_ylabel("Conjunto de datos", fontsize=8)

        cbar_ax = fig.add_axes([0.92, 0.12, 0.015, 0.75])
        vmin, vmax = _global_bounds(algo_mats.values())

        sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=plt.Normalize(vmin, vmax))
        sm.set_array([])

        fig.colorbar(sm, cax=cbar_ax, label=label)

        fig.suptitle(f"{label} — por algoritmo", fontsize=14, fontweight="bold", y=0.98)

        plt.tight_layout(rect=[0, 0, 0.90, 0.95])

        filename = f"metricgrid_{metric}.png"

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches="tight")
        plt.close()

        print(f"  [SAVED] {os.path.join(OUTPUT_DIR, filename)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generador de mapas de calor de cobertura de conjuntos (métrica C) para MONOMER.")

    parser.add_argument("--setup", choices=["small", "big"], default="big", help="configuración de experimento pequeña o completa")

    parser.add_argument("--plot_type", choices=["matrix", "suite", "biggrid", "pivotgrid", "metricgrid"], required=True, help="Type of plot to generate")

    parser.add_argument("--diff_mode", choices=DIFF_MODES, default=None, help="raw, abs or pct. If omitted, all three are generated.")

    parser.add_argument("--metric", choices=ALL_METRICS, default=None, help="Metric for metricgrid mode. If omitted, all metrics are generated.")

    parser.add_argument("--dataset", default=None, help="Dataset filter for matrix/suite mode.")

    parser.add_argument("--model", default=None, help="Model filter for matrix/suite mode.")

    parser.add_argument("--algo_A", default=None, help="Algorithm A for suite mode.")

    parser.add_argument("--algo_B", default=None, help="Algorithm B for suite mode.")

    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    diff_modes = [args.diff_mode] if args.diff_mode else list(DIFF_MODES)

    for diff_mode in diff_modes:
        args.diff_mode = diff_mode

        print("\n" + "=" * 60)
        print(" SET COVERAGE PLOTTER")
        print(f"  Tipo:   {args.plot_type}")
        print(f"  Diferencia: {diff_mode}")
        print(f"  Configuración: {args.setup}")

        if args.dataset:
            print(f"  Conjunto de datos: {args.dataset}")

        if args.model:
            print(f"  Modelo:   {args.model}")

        if args.algo_A:
            print(f"  Algoritmo A: {args.algo_A}")

        if args.algo_B:
            print(f"  Algoritmo B: {args.algo_B}")

        print("=" * 60 + "\n")

        if args.plot_type == "matrix":
            build_matrix(args)

        elif args.plot_type == "suite":
            build_suite(args)

        elif args.plot_type == "biggrid":
            build_big_grid(args)

        elif args.plot_type == "pivotgrid":
            build_pivot_grid(args)

        elif args.plot_type == "metricgrid":
            build_metric_grid(args)

    print(f"\nDone. Results in {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()