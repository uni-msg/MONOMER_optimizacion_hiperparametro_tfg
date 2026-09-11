#!/usr/bin/env python3
"""
MONOMER - Hyperparameter vs objectives analysis

For each classifier, generates one PNG with one subplot per mutable numeric
hyperparameter:
    X = hyperparameter value
    Y = Balanced Accuracy
    Color = Leanness (number of selected features)
    Marker = dataset

All five outer-CV folds are combined per dataset. *_final.csv files are
never used.
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
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]
DATASET_LABELS = {
    "brca": "BRCA",
    "luad_lusc": "LUAD-LUSC",
    "tcga_kir": "KIR",
    "tcga_ov": "OV",
}
DATASET_MARKERS = {
    "brca": "o",
    "luad_lusc": "s",
    "tcga_kir": "^",
    "tcga_ov": "D",
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


def find_experiment_path(work_dir, dataset, model_dir):
    base = os.path.join(work_dir, dataset, "mrna", model_dir, "5_folds")
    if not os.path.isdir(base):
        return None

    candidates = []
    for name in os.listdir(base):
        path = os.path.join(base, name)
        if not os.path.isdir(path) or not name.startswith("HPE_NSGA2"):
            continue
        pareto = os.path.join(path, "hofs", "Pareto")
        score = sum(
            os.path.isfile(os.path.join(
                pareto, f"solution_hyperparameters_fold_{fold}.csv"
            ))
            for fold in range(N_FOLDS)
        )
        candidates.append((score, path))

    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][1]


def solution_file(exp_path, kind, fold):
    return os.path.join(
        exp_path, "hofs", "Pareto",
        f"solution_{kind}_fold_{fold}.csv"
    )


def load_dataset(experiment_path, dataset):
    frames = []
    for fold in range(N_FOLDS):
        hp_path = solution_file(experiment_path, "hyperparameters", fold)
        fit_path = solution_file(experiment_path, "fitnesses", fold)

        if not os.path.isfile(hp_path) or not os.path.isfile(fit_path):
            print(f"      [WARN] {dataset.upper()} fold {fold}: missing file")
            continue

        try:
            hp = pd.read_csv(hp_path).reset_index(drop=True)
            fit = pd.read_csv(fit_path).reset_index(drop=True)
        except Exception as exc:
            print(f"      [WARN] {dataset.upper()} fold {fold}: {exc}")
            continue

        if hp.empty or fit.empty:
            continue
        if len(hp) != len(fit):
            print(
                f"      [WARN] {dataset.upper()} fold {fold}: row mismatch "
                f"({len(hp)} vs {len(fit)}), skipped"
            )
            continue

        # Prefix fitness columns so they cannot collide with hyperparameter names.
        fit = fit.add_prefix("_fitness_")
        df = pd.concat([hp, fit], axis=1)
        df["_fold"] = fold
        df["_dataset"] = dataset
        frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def is_metadata_column(column):
    name = str(column).strip().lower()
    tokens = [
        "solution", "fitness", "objective", "balanced_accuracy", "bal_acc",
        "leanness", "fold", "index", "unnamed:", "rank", "crowding",
    ]
    return any(token in name for token in tokens)


def get_hyperparameter_columns(df):
    return [
        column for column in df.columns
        if not str(column).startswith("_") and not is_metadata_column(column)
    ]


def classify_type(series):
    values = series.dropna()
    if values.empty:
        return "categorical"
    strings = values.astype(str).str.strip().str.lower()
    if strings.isin(["true", "false", "yes", "no", "0", "1"]).all():
        return "boolean"
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().all():
        arr = numeric.to_numpy(dtype=float)
        return "integer" if np.allclose(arr, np.round(arr)) else "float"
    return "categorical"


def unique_values(series):
    values = series.dropna()
    if values.empty:
        return []
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().all():
        return np.unique(numeric.to_numpy(dtype=float)).tolist()
    return values.astype(str).unique().tolist()


def is_mutable(df, column):
    return len(unique_values(df[column])) > 1


def looks_log_scale(series):
    values = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    values = np.abs(values[np.isfinite(values)])
    if len(values) < 5 or np.any(values <= 0):
        return False
    return values.max() / values.min() >= 100


def pretty_name(name):
    return re.sub(r"\s+", " ", str(name).replace("_", " ")).strip()


def find_column(df, candidates):
    normalized = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    for column in df.columns:
        name = str(column).strip().lower()
        for candidate in candidates:
            if candidate.lower() in name:
                return column
    return None


def find_bal_acc_column(df):
    return find_column(df, [
        "_fitness_balanced_accuracy",
        "_fitness_bal_acc",
        "_fitness_balanced_acc",
        "balanced_accuracy",
        "bal_acc",
    ])


def find_leanness_column(df):
    return find_column(df, ["_fitness_leanness", "leanness"])


def plot_relation(ax, df, hyperparameter, bal_acc_col, leanness_col):
    x = pd.to_numeric(df[hyperparameter], errors="coerce")
    y = pd.to_numeric(df[bal_acc_col], errors="coerce")
    c = pd.to_numeric(df[leanness_col], errors="coerce")
    valid = x.notna() & y.notna() & c.notna()
    data = df.loc[valid, ["_dataset"]].copy()
    data["x"] = x.loc[valid].to_numpy()
    data["y"] = y.loc[valid].to_numpy()
    data["c"] = c.loc[valid].to_numpy()

    if data.empty:
        ax.text(0.5, 0.5, "No hay datos utilizables", ha="center", va="center", transform=ax.transAxes)
        return None

    last = None
    for dataset in DATASETS:
        subset = data[data["_dataset"] == dataset]
        if subset.empty:
            continue
        last = ax.scatter(
            subset["x"], subset["y"],
            c=subset["c"], cmap=LinearSegmentedColormap.from_list(
                "leanness_green_orange_red",
                [
                    "#16823B",  # low Leanness
                    "#F08A24",  # intermediate Leanness
                    "#C62828",  # high Leanness
                ],
            ),
            marker=DATASET_MARKERS[dataset],
            s=28, alpha=0.60,
            edgecolors="white", linewidths=0.35,
            label=DATASET_LABELS[dataset],
        )

    if looks_log_scale(df[hyperparameter]):
        ax.set_xscale("log")
        ax.set_xlabel(f"{pretty_name(hyperparameter)} (log scale)")
    else:
        ax.set_xlabel(pretty_name(hyperparameter))
    ax.set_ylabel("Precisión balanceada")
    ax.set_title(pretty_name(hyperparameter), fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.35)
    return last


def make_classifier_png(df, model, output_dir):
    hyperparameters = get_hyperparameter_columns(df)
    mutable_numeric = [
        c for c in hyperparameters
        if is_mutable(df, c) and classify_type(df[c]) in {"float", "integer"}
    ]

    print(f"    Hyperparameters found: {len(hyperparameters)}")
    print("    Numeric mutable parameters: " + (", ".join(map(str, mutable_numeric)) if mutable_numeric else "NONE"))

    bal_acc_col = find_bal_acc_column(df)
    leanness_col = find_leanness_column(df)
    if bal_acc_col is None or leanness_col is None:
        print("    [!] Could not identify Balanced Accuracy and/or Leanness columns.")
        print("    Fitness columns:", [c for c in df.columns if str(c).startswith("_fitness_")])
        return

    print(f"    Balanced Accuracy column: {bal_acc_col}")
    print(f"    Leanness column: {leanness_col}")
    if not mutable_numeric:
        return

    n = len(mutable_numeric)
    ncols = 1 if n == 1 else (2 if n <= 6 else 3)
    nrows = int(np.ceil(n / ncols))
    # Reserve a dedicated column on the right for the Leanness colorbar.
    # This prevents it from overlapping any subplot.
    fig = plt.figure(
        figsize=(7.8 * ncols + 0.9, 5.9 * nrows)
    )

    gs = GridSpec(
        nrows,
        ncols + 1,
        figure=fig,
        width_ratios=[1] * ncols + [0.055],
        wspace=0.28,
        hspace=0.32,
    )

    axes = []

    for row in range(nrows):
        for col in range(ncols):
            axes.append(
                fig.add_subplot(gs[row, col])
            )

    colorbar_ax = fig.add_subplot(
        gs[:, -1]
    )

    fig.suptitle(
        f"{MODEL_LABELS[model]} — Hiperparámetros vs Objetivos",
        fontsize=17,
        fontweight="bold",
        y=0.98,
    )

    last = None

    for ax, hp in zip(axes, mutable_numeric):
        result = plot_relation(
            ax,
            df,
            hp,
            bal_acc_col,
            leanness_col,
        )

        if result is not None:
            last = result

    # Increase font sizes for combined figures with more than two hyperparameters.
    if n > 2:
        for ax in axes[:len(mutable_numeric)]:
            ax.title.set_fontsize(14)
            ax.xaxis.label.set_fontsize(12)
            ax.yaxis.label.set_fontsize(12)
            ax.tick_params(axis="both", labelsize=10)

    for ax in axes[len(mutable_numeric):]:
        ax.axis("off")

    # Dataset is represented by marker shape because color represents
    # the continuous Leanness value.
    handles = [
        Line2D(
            [0],
            [0],
            marker=DATASET_MARKERS[d],
            linestyle="",
            markerfacecolor="gray",
            markeredgecolor="white",
            markersize=8,
            label=DATASET_LABELS[d],
        )
        for d in DATASETS
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=9,
        bbox_to_anchor=(0.5, 0.005),
    )

    if last is not None:
        cb = fig.colorbar(
            last,
            cax=colorbar_ax,
        )
        cb.set_label(
            "Leanness (number of selected features)",
            rotation=270,
            labelpad=16,
        )

    # No explanatory sentence is added below the plots.

    fig.tight_layout(
        rect=[0, 0.055, 1, 0.95]
    )

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{model}_hyperparameters_vs_objectives.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"    [SAVED] {path}")

    # Individual plots are also useful for the TFG.
    individual_dir = os.path.join(output_dir, "individual", model)
    os.makedirs(individual_dir, exist_ok=True)
    for hp in mutable_numeric:
        fig, ax = plt.subplots(figsize=(11, 7.8))
        scatter = plot_relation(ax, df, hp, bal_acc_col, leanness_col)
        fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9)
        if scatter is not None:
            cb = fig.colorbar(scatter, ax=ax, pad=0.02)
            cb.set_label("Leanness (number of selected features)", rotation=270, labelpad=16)
        fig.suptitle(pretty_name(hp), fontsize=15, fontweight="bold")
        fig.tight_layout(rect=[0, 0.06, 1, 0.95])
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(hp))
        fig.savefig(os.path.join(individual_dir, f"{safe}_vs_objectives.pdf"), bbox_inches="tight")
        plt.close(fig)


def analyze_model(work_dir, model, output_dir):
    print("\n" + "=" * 75)
    print(f" {MODEL_LABELS[model]}")
    print("=" * 75)
    frames = []
    for dataset in DATASETS:
        print(f"\n  {dataset.upper()}")
        exp = find_experiment_path(work_dir, dataset, MODELS[model])
        if exp is None:
            print("    [-] HPE experiment not found")
            continue
        print(f"    Experiment: {exp}")
        df = load_dataset(exp, dataset)
        if df.empty:
            print("    [-] No fold data found")
            continue
        print(f"    Solutions loaded: {len(df)}")
        print(f"    Folds: {sorted(df['_fold'].unique().tolist())}")
        frames.append(df)
    if frames:
        make_classifier_png(pd.concat(frames, ignore_index=True), model, output_dir)
    else:
        print(f"\n  [!] No data available for {MODEL_LABELS[model]}")


def main():
    parser = argparse.ArgumentParser(description="MONOMER hyperparameter vs objectives plots")
    parser.add_argument("--work-dir", default=os.getcwd())
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--model", choices=list(MODELS), default=None)
    args = parser.parse_args()

    work_dir = os.path.abspath(args.work_dir)
    output_dir = os.path.abspath(args.output_dir) if args.output_dir else os.path.join(
        work_dir, "tuning_reports", "hyperparameters_vs_objectives"
    )
    os.makedirs(output_dir, exist_ok=True)

    models = [args.model] if args.model else list(MODELS)
    print("\n" + "=" * 75)
    print(" MONOMER — HYPERPARAMETER VS OBJECTIVES")
    print("=" * 75)
    print(f"Work directory : {work_dir}")
    print(f"Output         : {output_dir}")
    print("Conjuntos de datos : BRCA, LUAD-LUSC, KIR, OV")
    print("Datos         : solo folds externos 0–4")
    print("Archivos finales : EXCLUIDOS")
    print("Parámetros fijos : EXCLUIDOS")
    print("Categóricos    : EXCLUIDOS")
    print("=" * 75)

    for model in models:
        analyze_model(work_dir, model, output_dir)

    print("\n" + "=" * 75)
    print(" HECHO")
    print("=" * 75)


if __name__ == "__main__":
    main()
