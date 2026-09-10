import os
import sys
import glob
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from rich.console import Console
from rich.table import Table
from rich import box

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.hyperbox.hyperbox import ConcreteHyperbox0B
from util.cross_hypervolume.cross_hypervolume import cross_hypervolume
from saved_solutions.run_fold_jaccard import compute_jaccard_from_lists

console = Console()

CLASSIFIER_DIR_MAP = {
    "svm": "leanness_svm_bal_acc",
    "naive_bayes": "NB_bal_acc_leanness",
    "RF": "RF_bal_acc_leanness",
}

DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]
CLASSIFIERS = ["svm", "naive_bayes", "RF"]
FI_MODES = ["none", "lasso"]

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work'))

NSGA2_VARIANTS = [
    ("nsga2", "CrowdFull", "_(none,none)"),
    ("nsga2_ch", "CrowdCI", "_(MV_lassoFI,none)"),
    ("nsga2_chs", "CrowdCICR", "_(MV_lassoFI,none)"),
]


def extract_metrics(opt_dir):
    hof_dir = os.path.join(opt_dir, "hofs", "Pareto")
    if not os.path.exists(hof_dir):
        return None, None
    fit_files = sorted(glob.glob(os.path.join(hof_dir, "solution_fitnesses_fold_*.csv")))
    feat_files = sorted(glob.glob(os.path.join(hof_dir, "solution_features_fold_*.csv")))
    if not fit_files or not feat_files:
        return None, None

    cross_hv_list, fold_jaccards = [], []
    for fit_f, feat_f in zip(fit_files, feat_files):
        try:
            df_fit = pd.read_csv(fit_f)
            df_feat = pd.read_csv(feat_f)
            feature_names = df_feat.columns.tolist()
            gene_lists = [
                [name for name, val in zip(feature_names, row) if val == 1]
                for _, row in df_feat.iterrows()
            ]
            fold_jaccards.append(compute_jaccard_from_lists(gene_lists))

            train_col = next((c for c in df_fit.columns if "inner_cv" in c or "train_" in c), None)
            test_col = next((c for c in df_fit.columns if "test_" in c), None)
            lean_col = next((c for c in df_fit.columns if "leanness" in c), None)

            if train_col and test_col and lean_col:
                tr_boxes = [
                    ConcreteHyperbox0B.create_by_b_vals((r[train_col], r[lean_col]))
                    for _, r in df_fit.iterrows()
                ]
                te_boxes = [
                    ConcreteHyperbox0B.create_by_b_vals((r[test_col], r[lean_col]))
                    for _, r in df_fit.iterrows()
                ]
                cross_hv_list.append(cross_hypervolume(tr_boxes, te_boxes))
        except Exception:
            return None, None

    if not cross_hv_list or not fold_jaccards:
        return None, None
    return float(np.mean(cross_hv_list)), float(np.mean(fold_jaccards))


def collect_experiments(scale):
    records = []
    for dataset in DATASETS:
        for clf in CLASSIFIERS:
            clf_dir = CLASSIFIER_DIR_MAP[clf]
            for fi_mode in FI_MODES:
                if scale == "mini":
                    base = os.path.join(WORK, f"{dataset}_mini", "mrna", clf_dir, "2_folds")
                    fi_tag = "(MV_lassoFI,none)" if fi_mode == "lasso" else "(none,none)"
                    pattern = os.path.join(base, f"*v8_less_tolerance_mini_{fi_tag}")
                else:
                    base = os.path.join(WORK, dataset, "mrna", clf_dir, "5_folds")
                    if fi_mode == "lasso":
                        pattern = os.path.join(base, "*v8_less_tolerance_big_lasso_*")
                    else:
                        pattern = os.path.join(base, "*v8_less_tolerance_big_(none,none)")

                matches = sorted(glob.glob(pattern))
                if not matches:
                    continue
                opt_dir = matches[-1]
                lcb, jac = extract_metrics(opt_dir)
                if lcb is not None:
                    records.append({
                        "Dataset_Clean": dataset,
                        "Model": clf,
                        "FI_Mode": fi_mode,
                        "LCB": lcb,
                        "Jac": jac,
                    })
    return records


def validate_proxy(output_dir):
    console.print(f"\n[bold cyan]=== VALIDACIÓN DE FIDELIDAD (MULTI-FIDELITY PROXY) ===[/bold cyan]")

    mini_records = collect_experiments("mini")
    big_records = collect_experiments("big")

    console.print(f"[dim]Mini experimentos encontrados: {len(mini_records)}[/dim]")
    console.print(f"[dim]Big experimentos encontrados: {len(big_records)}[/dim]")

    if not mini_records or not big_records:
        console.print("[bold red][!] Error: No se encontraron experimentos en uno o ambos grupos.[/bold red]")
        sys.exit(1)

    df_mini = pd.DataFrame(mini_records).rename(columns={"LCB": "LCB_Mini", "Jac": "Jac_Mini"})
    df_big = pd.DataFrame(big_records).rename(columns={"LCB": "LCB_Big", "Jac": "Jac_Big"})

    df_merged = pd.merge(
        df_mini, df_big,
        on=["Dataset_Clean", "Model", "FI_Mode"],
        how="inner",
    )

    if len(df_merged) < 3:
        console.print("[bold red][!] Error: Se necesitan al menos 3 experimentos comunes para calcular Spearman.[/bold red]")
        console.print(f"    Coincidentes encontrados: {len(df_merged)}")
        sys.exit(1)

    df_merged["Label"] = (
        df_merged["Dataset_Clean"] + "_" + df_merged["Model"] + "_" + df_merged["FI_Mode"]
    )

    spearman_lcb, p_val_lcb = spearmanr(df_merged["LCB_Mini"], df_merged["LCB_Big"])
    spearman_jac, p_val_jac = spearmanr(df_merged["Jac_Mini"], df_merged["Jac_Big"])

    table = Table(
        title=f"Métricas de Fidelidad (Spearman ρ) | N={len(df_merged)} pares",
        style="magenta",
    )
    table.add_column("Métrica", style="cyan", justify="left")
    table.add_column("Correlación (ρ)", style="green", justify="center")
    table.add_column("P-Value", justify="right")
    table.add_column("Veredicto", style="yellow")

    def get_verdict(rho):
        if rho >= 0.85:
            return "[bold green]Excelente Proxy[/bold green]"
        if rho >= 0.70:
            return "[green]Buen Proxy[/green]"
        if rho >= 0.50:
            return "[yellow]Proxy Débil (Cuidado)[/yellow]"
        return "[bold red]No Correlaciona (Inútil)[/bold red]"

    table.add_row("LCB (Robustez CHV)", f"{spearman_lcb:.4f}", f"{p_val_lcb:.4e}", get_verdict(spearman_lcb))
    table.add_row("Jaccard (Variedad)", f"{spearman_jac:.4f}", f"{p_val_jac:.4e}", get_verdict(spearman_jac))

    console.print(table)

    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.scatter(df_merged["LCB_Mini"], df_merged["LCB_Big"],
                color="#377EB8", s=100, edgecolor="black", zorder=3)
    m, b = np.polyfit(df_merged["LCB_Mini"], df_merged["LCB_Big"], 1)
    plt.plot(df_merged["LCB_Mini"], m * df_merged["LCB_Mini"] + b,
             color="gray", linestyle="--", zorder=2)
    for i, txt in enumerate(df_merged["Label"]):
        plt.annotate(
            txt,
            (df_merged["LCB_Mini"].iloc[i], df_merged["LCB_Big"].iloc[i]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
        )
    plt.title(f"Correlación LCB (ρ = {spearman_lcb:.2f})", fontweight="bold")
    plt.xlabel("CHV en Experimento MINI (Pop 50 / 5k Evals)")
    plt.ylabel("CHV en Experimento BIG (Pop 500 / 500k Evals)")
    plt.grid(True, linestyle=":", alpha=0.6)

    plt.subplot(1, 2, 2)
    plt.scatter(df_merged["Jac_Mini"], df_merged["Jac_Big"],
                color="#E41A1C", s=100, edgecolor="black", zorder=3)
    m_j, b_j = np.polyfit(df_merged["Jac_Mini"], df_merged["Jac_Big"], 1)
    plt.plot(df_merged["Jac_Mini"], m_j * df_merged["Jac_Mini"] + b_j,
             color="gray", linestyle="--", zorder=2)
    for i, txt in enumerate(df_merged["Label"]):
        plt.annotate(
            txt,
            (df_merged["Jac_Mini"].iloc[i], df_merged["Jac_Big"].iloc[i]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
        )
    plt.title(f"Correlación Jaccard (ρ = {spearman_jac:.2f})", fontweight="bold")
    plt.xlabel("Jaccard en Experimento MINI")
    plt.ylabel("Jaccard en Experimento BIG")
    plt.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    out_file = os.path.join(output_dir, "proxy_correlation_plot.png")
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()

    console.print(f"\n[+] Gráfico de correlación guardado en: [cyan]{out_file}[/cyan]")
    console.print(f"[+] Pares equiparados: {len(df_merged)}")
    for _, row in df_merged.iterrows():
        console.print(
            f"    {row['Dataset_Clean']:12s} {row['Model']:12s} "
            f"{row['FI_Mode']:6s}  mini=({row['LCB_Mini']:.4f},{row['Jac_Mini']:.4f})  "
            f"big=({row['LCB_Big']:.4f},{row['Jac_Big']:.4f})"
        )


def collect_mini_variants():
    records = []
    for dataset in DATASETS:
        for clf in CLASSIFIERS:
            clf_dir = CLASSIFIER_DIR_MAP[clf]
            base = os.path.join(WORK, f"{dataset}_mini", "mrna", clf_dir, "2_folds")

            for name, variant, suffix in NSGA2_VARIANTS:
                pattern = os.path.join(base, f"NSGA2*{variant}*{suffix}")
                matches = sorted(glob.glob(pattern))
                if not matches:
                    continue
                lcb, jac = extract_metrics(matches[-1])
                if lcb is not None:
                    records.append({
                        "Dataset": dataset, "Model": clf,
                        "Algoritmo": name, "Tipo": "NSGA2",
                        "FI_Mode": "lasso" if "MV_lassoFI" in suffix else "none",
                        "LCB": lcb, "Jac": jac,
                    })

            for fi_mode in FI_MODES:
                fi_tag = "(MV_lassoFI,none)" if fi_mode == "lasso" else "(none,none)"
                pattern = os.path.join(base, f"*v8_less_tolerance_mini_{fi_tag}")
                matches = sorted(glob.glob(pattern))
                if not matches:
                    continue
                lcb, jac = extract_metrics(matches[-1])
                if lcb is not None:
                    algo_name = "moabc" if fi_mode == "lasso" else "moabc_no_lasso"
                    records.append({
                        "Dataset": dataset, "Model": clf,
                        "Algoritmo": algo_name, "Tipo": "MOABC",
                        "FI_Mode": fi_mode,
                        "LCB": lcb, "Jac": jac,
                    })

    return records


def analyze_rank_consistency(output_dir):
    console.print(f"\n[bold cyan]=== CONSISTENCIA DE RANKINGS (MINI) ===[/bold cyan]")

    mini_variants = collect_mini_variants()
    if not mini_variants:
        console.print("[bold red][!] No se encontraron variantes mini.[/bold red]")
        return

    df = pd.DataFrame(mini_variants)
    groups = df.groupby(["Dataset", "Model"])
    n_groups = len(groups)
    algorithms = sorted(df["Algoritmo"].unique())
    n_algo = len(algorithms)

    algo_idx = {a: i for i, a in enumerate(algorithms)}
    rank_matrix = np.zeros((n_groups, n_algo))
    group_labels = []

    for gi, ((ds, mod), grp) in enumerate(groups):
        grp = grp.sort_values("LCB", ascending=False)
        group_labels.append(f"{ds}_{mod}")
        for rank, (_, row) in enumerate(grp.iterrows(), start=1):
            rank_matrix[gi, algo_idx[row["Algoritmo"]]] = rank

    from scipy.stats import chi2 as chi2_dist
    m = n_groups
    n = n_algo
    rank_sums = rank_matrix.sum(axis=0)
    mean_rank_sum = rank_sums.mean()
    S = ((rank_sums - mean_rank_sum) ** 2).sum()
    w = 12 * S / (m ** 2 * (n ** 3 - n))
    chi2_val = m * (n - 1) * w
    p_w = 1.0 - chi2_dist.cdf(chi2_val, df=n - 1)
    mean_ranks = rank_matrix.mean(axis=0)

    short_labels = {
        "brca_svm": "B_SVM", "brca_naive_bayes": "B_NB", "brca_RF": "B_RF",
        "luad_lusc_svm": "L_SVM", "luad_lusc_naive_bayes": "L_NB", "luad_lusc_RF": "L_RF",
        "tcga_kir_svm": "K_SVM", "tcga_kir_naive_bayes": "K_NB", "tcga_kir_RF": "K_RF",
        "tcga_ov_svm": "O_SVM", "tcga_ov_naive_bayes": "O_NB", "tcga_ov_RF": "O_RF",
    }
    table = Table(title=f"Ranking por CHV en MINI | W={w:.4f}, p={p_w:.4e}",
                  box=box.ROUNDED, style="cyan")
    table.add_column("Algoritmo", style="yellow")
    table.add_column("R.Medio", justify="center")
    table.add_column("Tipo", style="green")
    for gi, gl in enumerate(group_labels):
        table.add_column(short_labels.get(gl, gl), justify="center", style="dim")

    for ai, algo in enumerate(algorithms):
        row_data = df[df["Algoritmo"] == algo].iloc[0]
        tipo = row_data["Tipo"]
        table.add_row(algo, f"{mean_ranks[ai]:.2f}", tipo, *[
            str(int(rank_matrix[gi, ai])) for gi in range(n_groups)
        ])

    console.print(table)
    console.print("\n[dim]CHV medios por algoritmo y grupo:[/dim]")
    for ai, algo in enumerate(algorithms):
        vals = []
        for gi, (ds, md) in enumerate(groups.groups.keys()):
            val = df[(df["Dataset"] == ds) & (df["Model"] == md) & (df["Algoritmo"] == algo)]["LCB"].values
            vals.append(f"{val[0]:.3f}" if len(val) > 0 else "-")
        console.print(f"  {algo:14s}: " + " ".join(vals))

    console.print(f"\nW de Kendall = [bold]{w:.4f}[/bold] (p={p_w:.4e})")
    if w >= 0.80:
        console.print("[green]→ Concordancia Muy Alta: las 5 variantes se ordenan igual en todos los grupos[/green]")
    elif w >= 0.60:
        console.print("[yellow]→ Concordancia Moderada: hay desacuerdos parciales[/yellow]")
    else:
        console.print("[red]→ Concordancia Baja: el orden varía según dataset/clasificador[/red]")

    mini_big = compare_moabc_ordering()
    if mini_big:
        table2 = Table(title="Orden relativo MOABC none vs lasso: MINI vs BIG",
                       box=box.ROUNDED, style="magenta")
        table2.add_column("Grupo", style="cyan")
        table2.add_column("Mini: mejor", justify="center")
        table2.add_column("Big: mejor", justify="center")
        table2.add_column("¿Coincide?", justify="center")
        n_ok = sum(1 for r in mini_big if r["coincide"])
        for r in mini_big:
            table2.add_row(r["grupo"], r["mini_best"], r["big_best"],
                           "[green]✓[/green]" if r["coincide"] else "[red]✗[/red]")
        console.print(table2)
        console.print(f"\n[bold]Coincidencias: {n_ok}/{len(mini_big)} grupos[/bold]")


def compare_moabc_ordering():
    mini = collect_experiments("mini")
    big = collect_experiments("big")
    df_mini = pd.DataFrame(mini)
    df_big = pd.DataFrame(big)

    results = []
    for ds in DATASETS:
        for clf in CLASSIFIERS:
            m = df_mini[(df_mini["Dataset_Clean"] == ds) & (df_mini["Model"] == clf)]
            b = df_big[(df_big["Dataset_Clean"] == ds) & (df_big["Model"] == clf)]
            if len(m) < 2 or len(b) < 2:
                continue
            mini_best = "lasso" if m.loc[m["FI_Mode"] == "lasso", "LCB"].values[0] > m.loc[m["FI_Mode"] == "none", "LCB"].values[0] else "none"
            big_best = "lasso" if b.loc[b["FI_Mode"] == "lasso", "LCB"].values[0] > b.loc[b["FI_Mode"] == "none", "LCB"].values[0] else "none"
            results.append({
                "grupo": f"{ds}_{clf}",
                "mini_best": mini_best,
                "big_best": big_best,
                "coincide": mini_best == big_best,
            })
    return results


if __name__ == "__main__":
    out_dir = os.path.join(os.getcwd(), "tuning_reports", "Proxy_Validation")
    validate_proxy(out_dir)
    analyze_rank_consistency(out_dir)
