import os
import sys
import glob
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))
sys.path.append(os.path.join(PROJECT_ROOT, 'py'))

from util.hyperbox.hyperbox import ConcreteHyperbox0B
from util.cross_hypervolume.cross_hypervolume import hypervolume
from util.cross_hypervolume.cross_hypervolume import cross_hypervolume

DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]

MODELS = {
    "naive_bayes": "NB_bal_acc_leanness",
    "svm": "leanness_svm_bal_acc",
    "RF": "RF_bal_acc_leanness",
    "logistic": "leanness_logit100_bal_acc"
}

HPE_NAME = "HPE_NSGA2_k3_pop{pop}_uni0-50_gen1000_CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)"


def get_hpe_path(base_dir, dataset, model, pop):
    return os.path.join(base_dir, dataset, "mrna", MODELS[model], "5_folds", HPE_NAME.format(pop=pop))


def calculate_offline_hypervolume(front_coordinates):
    if not front_coordinates:
        return 0.0
    hyperboxes = [ConcreteHyperbox0B.create_by_b_vals((float(p[0]), float(p[1]))) for p in front_coordinates]
    return hypervolume(hyperboxes)


def read_jsonl_log(filepath):
    generations = []
    hvs = []

    if not os.path.exists(filepath):
        return pd.DataFrame()

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                generation = data.get('generation')
                individuals = data.get('individuals', [])

                if generation is None or not individuals:
                    continue

                front = []

                for individual in individuals:
                    fitness = individual.get('fitness')

                    if not fitness or len(fitness) < 2:
                        continue

                    bal_acc = fitness[0]
                    leanness = fitness[1]

                    if bal_acc is None or leanness is None:
                        continue

                    front.append((float(bal_acc), float(leanness)))

                if not front:
                    continue

                hv = calculate_offline_hypervolume(front)
                generations.append(int(generation))
                hvs.append(hv)

            except (json.JSONDecodeError, TypeError, ValueError, KeyError):
                continue

    return pd.DataFrame({"generation": generations, "inner_hypervolume": hvs})


def find_history_files(exp_path):
    pareto_dir = os.path.join(exp_path, "hofs", "Pareto")
    files = sorted(glob.glob(os.path.join(pareto_dir, "ga_evolution_history_fold_*.jsonl")))
    if files:
        return files
    return sorted(glob.glob(os.path.join(exp_path, "ga_evolution_history_fold_*.jsonl")))


def calculate_jaccard(features_dfs):
    if len(features_dfs) < 2:
        return 0.0, 0.0

    sets = []

    for df in features_dfs:
        for _, row in df.iterrows():
            selected = set(str(col) for col, value in row.items() if value not in [0, 0.0, False, "0", "0.0"])
            sets.append(selected)

    if len(sets) < 2:
        return 0.0, 0.0

    values = []

    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            union = sets[i] | sets[j]

            if not union:
                continue

            intersection = sets[i] & sets[j]
            values.append(len(intersection) / len(union))

    if not values:
        return 0.0, 0.0

    return float(np.mean(values)), float(np.std(values))


def extract_final_metrics(exp_path):
    pareto_dir = os.path.join(exp_path, "hofs", "Pareto")

    if not os.path.exists(pareto_dir):
        return None

    feature_files = sorted(glob.glob(os.path.join(pareto_dir, "solution_features_fold_*.csv")))
    fitness_files = sorted(glob.glob(os.path.join(pareto_dir, "solution_fitnesses_fold_*.csv")))

    if not feature_files or not fitness_files:
        return None

    feature_dfs = [pd.read_csv(path) for path in feature_files]
    fitness_dfs = [pd.read_csv(path) for path in fitness_files]

    jac_m, jac_s = calculate_jaccard(feature_dfs)
    chv_values = []

    for df in fitness_dfs:
        train_col = next((c for c in df.columns if "inner_cv" in c or "train_" in c), None)
        test_col = next((c for c in df.columns if "test_" in c), None)
        lean_col = next((c for c in df.columns if "leanness" in c.lower() and "soft" not in c.lower()), None)

        if not train_col or not test_col or not lean_col:
            continue

        train_points = [(float(row[train_col]), float(row[lean_col])) for _, row in df.iterrows() if pd.notna(row[train_col]) and pd.notna(row[lean_col])]
        test_points = [(float(row[test_col]), float(row[lean_col])) for _, row in df.iterrows() if pd.notna(row[test_col]) and pd.notna(row[lean_col])]

        if not train_points or not test_points:
            continue

        try:
            train_boxes = [ConcreteHyperbox0B.create_by_b_vals(p) for p in train_points]
            test_boxes = [ConcreteHyperbox0B.create_by_b_vals(p) for p in test_points]
            chv_values.append(cross_hypervolume(train_boxes, test_boxes))
        except Exception:
            continue

    if chv_values:
        chv_m = float(np.mean(chv_values))
        chv_s = float(np.std(chv_values))
    else:
        chv_m = 0.0
        chv_s = 0.0

    return {"jac_m": jac_m, "jac_s": jac_s, "chv_m": chv_m, "chv_s": chv_s}


def find_knee_point(generations, hvs):
    if len(generations) == 0:
        return None, None

    hvs_smooth = pd.Series(hvs).rolling(window=5, min_periods=1).mean().values
    g_min = np.min(generations)
    g_max = np.max(generations)
    h_min = np.min(hvs_smooth)
    h_max = np.max(hvs_smooth)

    if h_max == h_min or g_max == g_min:
        return generations[-1], hvs[-1]

    generations_norm = (generations - g_min) / (g_max - g_min)
    hvs_norm = (hvs_smooth - h_min) / (h_max - h_min)
    distances = hvs_norm - generations_norm
    knee_idx = np.argmax(distances)

    return generations[knee_idx], hvs[knee_idx]


def find_plateau_point(generations, hvs, threshold=0.98):
    if len(generations) == 0:
        return None, None

    hvs_smooth = pd.Series(hvs).rolling(window=5, min_periods=1).mean().values
    max_hv = np.max(hvs_smooth)
    target_hv = max_hv * threshold
    plateau_idx = np.argmax(hvs_smooth >= target_hv)

    return generations[plateau_idx], hvs[plateau_idx]


def plot_mission(base_dir):
    report_dir = os.path.join(base_dir, "tuning_reports", "hpe")
    os.makedirs(report_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print(" HPE — CONVERGENCE AND TRADE-OFF ANALYSIS")
    print("=" * 70)

    results = []

    for dataset in DATASETS:
        for model in MODELS:
            pop = 200 if model == "logistic" else 500
            exp_path = get_hpe_path(base_dir, dataset, model, pop)

            print(f"\n[+] {dataset.upper()} / {model}")
            print(f"    Path: {exp_path}")

            if not os.path.exists(exp_path):
                print("    [-] HPE folder not found")
                continue

            history_files = find_history_files(exp_path)

            if not history_files:
                print("    [-] No evolution history found")
                continue

            fold_dfs = []

            for history_file in history_files:
                df = read_jsonl_log(history_file)

                if not df.empty:
                    fold_dfs.append(df)

            if not fold_dfs:
                print("    [-] No usable history")
                continue

            base_generations = fold_dfs[0]["generation"].values
            valid_hvs = []

            for df in fold_dfs:
                if len(df) == len(base_generations) and np.array_equal(df["generation"].values, base_generations):
                    valid_hvs.append(df["inner_hypervolume"].values)
                elif len(df) > 0:
                    valid_hvs.append(np.interp(base_generations, df["generation"].values, df["inner_hypervolume"].values))

            if not valid_hvs:
                continue

            avg_hv = np.mean(valid_hvs, axis=0)

            knee_generation, knee_hv = find_knee_point(base_generations, avg_hv)
            plateau_generation, plateau_hv = find_plateau_point(base_generations, avg_hv)

            print(f"    Knee generation: {int(knee_generation):,}")
            print(f"    98% plateau generation: {int(plateau_generation):,}")

            metrics = extract_final_metrics(exp_path)

            if metrics:
                results.append({"dataset": dataset, "model": model, **metrics})

            plt.figure(figsize=(10, 7))

            plt.plot(base_generations, avg_hv, linewidth=2.5)
            plt.scatter(knee_generation, knee_hv, marker="*", s=180, edgecolor="black", zorder=5)
            plt.scatter(plateau_generation, plateau_hv, marker="o", s=80, edgecolor="black", zorder=5)

            plt.xlabel("Generation")
            plt.ylabel("Mean Inner CV Hypervolume")
            plt.title(f"HPE convergence — {dataset.upper()} / {model}", fontweight="bold")
            plt.grid(True, linestyle=":", alpha=0.7)
            plt.tight_layout()

            filename = f"hpe_convergence_{dataset}_{model}.png"
            plt.savefig(os.path.join(report_dir, filename), dpi=300)
            plt.close()

    if not results:
        print("\n[!] No final metrics available.")
        return

    df_results = pd.DataFrame(results)

    df_results.to_csv(os.path.join(report_dir, "hpe_metrics.csv"), index=False)

    plt.figure(figsize=(10, 10))

    for _, row in df_results.iterrows():
        label = f"{row['dataset']} / {row['model']}"

        plt.errorbar(
            row["jac_m"],
            row["chv_m"],
            xerr=row["jac_s"],
            yerr=row["chv_s"],
            fmt="o",
            markersize=9,
            capsize=4,
            label=label
        )

    plt.xlabel("Diversity / Stability — Mean Jaccard")
    plt.ylabel("Generalization — Mean Cross Hypervolume")
    plt.title("HPE — Final trade-off: diversity vs generalization", fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()

    plt.savefig(
        os.path.join(report_dir, "hpe_tradeoff_CHV_Jaccard.png"),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"\n[INFO] Results saved in:\n       {report_dir}")


if __name__ == "__main__":
    plot_mission(os.getcwd())