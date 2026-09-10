import os
import sys
import glob
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Headless para SSH
import matplotlib.pyplot as plt
import re
import numpy as np
from datetime import datetime
import argparse
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

# --- IMPORTACIONES DEL FRAMEWORK ORIGINAL ---
sys.path.append(os.path.join(os.getcwd(), 'py'))
try:
    from util.list_math import mean_all_vs_others, jaccard, top_k_positions, dice
    from util.components_transform import HigherKComponents
    from util.sequence_utils import to_common_labels
    from util.dataframes import sum_by_columns
    from util.hyperbox.hyperbox import ConcreteHyperbox0B
    from util.cross_hypervolume.cross_hypervolume import cross_hypervolume
    from saved_solutions.run_fold_jaccard import compute_jaccard_from_lists
    from plots.hof_utils import hof_used_features_fold_dfs, hof_fitness_dfs
except ImportError as e:
    print(f"Error importando módulos del framework: {e}")
    sys.exit(1)

console = Console()

# --- CONFIGURACIÓN ---
WORK_DIR = os.getcwd()
BASE_OUTPUT_DIR = os.path.join(WORK_DIR, "front_pairs")
ALLOWED_DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_kir3", "tcga_ov", "swedish"]
HI_CONTRAST_COLORS = ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#A65628', '#F781BF', '#999999', '#000000']

# --- MAPEO FAST ---
FAST_MODE_MAPPING = {
    "brca":      {"best_algo": "nsga2_ch",  "best_model": "svm"},
    "luad_lusc": {"best_algo": "nsga2_chs", "best_model": "naive_bayes"},
    "tcga_kir":  {"best_algo": "nsga2",     "best_model": "RF"},
    "tcga_ov":   {"best_algo": "nsga2",     "best_model": "svm"}
}

# --- UTILIDADES DE NOMENCLATURA ---

def get_expected_nsga_name(base_algo, pop, gen, inner_folds):
    """Reconstruye el nombre exacto de la carpeta de NSGA-II según los parámetros."""
    if base_algo == "nsga2":
        return f"NSGA2_k{inner_folds}_pop{pop}_uni0-50_gen{gen}_CrowdFull_c0.33_m1.0flip_(none,none)"
    elif base_algo == "nsga2_ch":
        return f"NSGA2_k{inner_folds}_pop{pop}_uni0-50_gen{gen}_CrowdCI_c0.33_m1.0flip_(MV_lassoFI,none)"
    elif base_algo == "nsga2_chs":
        return f"NSGA2_k{inner_folds}_pop{pop}_uni0-50_gen{gen}_CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)"
    elif base_algo == "hpe_nsga2_chs":
        return f"HPE_NSGA2_k{inner_folds}_pop{pop}_uni0-50_gen{gen}_CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)"
    return ""

def shorten_exp_name(name):
    """Traduce los nombres de carpeta a etiquetas semánticas para la leyenda."""
    n = name.lower()
    prefix = "OLD_" if "old_" in n else ""
    
    # Búsqueda robusta del nick ignorando el sufijo final entre paréntesis (Soporta Lasso, Anova o None)
    moabc_match = re.search(r'moabc_p\d+_ev\d+_de(\d+)_do(\d+)_l\d+_(.+?)_\(.*\)', n)
    if moabc_match:
        de, do, nick = moabc_match.groups()
        return f"{prefix}MOABC [{nick}] (dE{de}/dO{do})"
        
    if "abc" in n or "moabc" in n:
        if "niche" in n: return f"{prefix}MOABC_niche"
        return f"{prefix}MOABC_std"
        
    nsga_match = re.search(r'nsga2_.+pop(\d+)', n)
    pop_str = f" [p{nsga_match.group(1)}]" if nsga_match else ""
    if "nsga" in n:
        if "symm" in n: return f"{prefix}NSGA2_CHS{pop_str}"
        elif "ci" in n: return f"{prefix}NSGA2_CH{pop_str}"
        else: return f"{prefix}NSGA2_Std{pop_str}"
        
    if "lasso" in n: return f"{prefix}Lasso"
    if "guided" in n: return f"{prefix}GuidedFwd"
    if "rfe" in n: return f"{prefix}RFE"
    return name[:15] + "..." if len(name) > 15 else name

# --- MATEMÁTICAS ---

def get_pareto_front(x, y):
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[mask], y[mask]
    if len(x) == 0: return np.array([]), np.array([])
    idx = np.lexsort((-y, x))
    x_s, y_s = x[idx], y[idx]
    p_x, p_y = [x_s[0]], [y_s[0]]
    for i in range(1, len(x_s)):
        if y_s[i] > p_y[-1]:
            p_x.append(x_s[i])
            p_y.append(y_s[i])
    return np.array(p_x), np.array(p_y)

def calculate_c_metric(x1, y1, x2, y2):
    fa_x, fa_y = get_pareto_front(x1, y1)
    fb_x, fb_y = get_pareto_front(x2, y2)
    if len(fa_x) == 0 or len(fb_x) == 0: return 0.0
    dominated = 0
    for bx, by in zip(fb_x, fb_y):
        if any((fa_x <= bx) & (fa_y >= by) & ((fa_x < bx) | (fa_y > by))):
            dominated += 1
    return dominated / len(fb_x)

def calc_jaccard_curve_exact(dfs):
    if len(dfs) < 2: return [], []
    fold_counts = [sum_by_columns(df) for df in dfs]
    fold_counts = to_common_labels(fold_counts)
    fold_counts = [pd.Series(li).fillna(0).tolist() for li in fold_counts]
    max_k = min([sum([a != 0 for a in fc]) for fc in fold_counts])
    if max_k <= 0: return [], []
    jac = []
    ks = list(range(1, max_k + 1))
    for k in ks:
        components_transform = HigherKComponents(k)
        fold_counts_k = [components_transform.apply(c) for c in fold_counts]
        jac.append(mean_all_vs_others(elems=fold_counts_k, measure_function=jaccard))
    return ks, jac

# --- CARGA Y PROCESAMIENTO OFFLINE ---

def get_data_from_exp(exp_path):
    target_dir = os.path.join(exp_path, "hofs", "Pareto")
    if not os.path.exists(target_dir):
        target_dir = os.path.join(exp_path, "hofs", "LASSO")
    if not os.path.exists(target_dir): return None
    
    try:
        feat_dfs = hof_used_features_fold_dfs(target_dir)
        fit_dfs = hof_fitness_dfs(target_dir)
    except: return None
    if not feat_dfs or not fit_dfs: return None

    data_by_fold = {}
    fold_chvs, fold_soft_chvs, fold_varieties, fold_dices = [], [], [], []
    
    for f_idx, (df_feat, df_fit) in enumerate(zip(feat_dfs, fit_dfs)):
        feature_names = df_feat.columns.tolist()
        gene_lists = [[name for name, val in zip(feature_names, row) if val == 1] for _, row in df_feat.iterrows()]
        fold_varieties.append(compute_jaccard_from_lists(gene_lists))
        n_sol = len(df_feat)
        if n_sol > 1:
            dice_sum = 0.0
            n_pairs = 0
            for r1 in range(n_sol):
                for r2 in range(r1 + 1, n_sol):
                    dice_sum += dice(df_feat.iloc[r1].tolist(), df_feat.iloc[r2].tolist())
                    n_pairs += 1
            fold_dices.append(dice_sum / n_pairs)
        else:
            fold_dices.append(1.0)
        
        train_acc_col = next((c for c in df_fit.columns if "inner_cv" in c or "train_" in c), None)
        test_acc_col = next((c for c in df_fit.columns if "test_" in c), None)
        lean_col = next((c for c in df_fit.columns if "leanness" in c and "soft" not in c), None)
        
        if train_acc_col and test_acc_col and lean_col:
            tr_boxes = [ConcreteHyperbox0B.create_by_b_vals((r[train_acc_col], r[lean_col])) for _, r in df_fit.iterrows()]
            te_boxes = [ConcreteHyperbox0B.create_by_b_vals((r[test_acc_col], r[lean_col])) for _, r in df_fit.iterrows()]
            fold_chvs.append(cross_hypervolume(tr_boxes, te_boxes))
        
        if train_acc_col and test_acc_col and lean_col:
            tr_soft = [ConcreteHyperbox0B.create_by_b_vals((r[train_acc_col], 1.0 / (1.0 + np.sqrt(max(0, round(1.0 / r[lean_col] - 1.0)))))) for _, r in df_fit.iterrows()]
            te_soft = [ConcreteHyperbox0B.create_by_b_vals((r[test_acc_col], 1.0 / (1.0 + np.sqrt(max(0, round(1.0 / r[lean_col] - 1.0)))))) for _, r in df_fit.iterrows()]
            fold_soft_chvs.append(cross_hypervolume(tr_soft, te_soft))
            
        x = df_feat.sum(axis=1).values
        y = df_fit[test_acc_col].values if test_acc_col else np.zeros(len(df_fit))
        s_idx = np.argsort(x)
        data_by_fold[f_idx] = {"x": x[s_idx], "y": y[s_idx]}

    jac_k, jac_v = calc_jaccard_curve_exact(feat_dfs)
    return {
        "folds": data_by_fold, "jaccard": {"k": jac_k, "v": jac_v},
        "metrics": {"chv_m": np.mean(fold_chvs) if fold_chvs else 0.0, "chv_s": np.std(fold_chvs) if fold_chvs else 0.0,
                    "schv_m": np.mean(fold_soft_chvs) if fold_soft_chvs else 0.0, "schv_s": np.std(fold_soft_chvs) if fold_soft_chvs else 0.0,
                    "var_m": np.mean(fold_varieties) if fold_varieties else 0.0, "var_s": np.std(fold_varieties) if fold_varieties else 0.0,
                    "dice_m": np.mean(fold_dices) if fold_dices else 0.0, "dice_s": np.std(fold_dices) if fold_dices else 0.0}
    }

# --- PLOTEO MÚLTIPLE ---

def plot_comparison(selected_exps, output_subdir, dataset_name, comp_name):
    os.makedirs(output_subdir, exist_ok=True)
    all_data = {}
    for name, path in selected_exps.items():
        data = get_data_from_exp(path)
        if data is not None:
            all_data[name] = data
        else:
            console.print(f"[bold red]  [!] ERROR: Carpeta corrupta o incompleta: {name}[/bold red]")
            console.print(f"      Ruta: {path}")

    exp_names = list(all_data.keys())
    if not exp_names:
        return

    short_names = [shorten_exp_name(n) for n in exp_names]
    active_folds = sorted(list(set(f for d in all_data.values() for f in d["folds"].keys())))

    is_small_test = len(active_folds) <= 2
    fig, axes = plt.subplots(2 if is_small_test else 3, 3, figsize=(18, 11 if is_small_test else 16))
    ax_f = axes.flatten()
    
    y_min_g, y_max_g, x_max_g = 1.0, 0.0, 0
    c_scores = {name: {} for name in exp_names}
    legend_handles, legend_labels = [], []
    idx_jac, idx_cloud, idx_pareto, idx_bars = (2,3,4,5) if is_small_test else (5,6,7,8)

    for i in range(len(ax_f)):
        if i not in active_folds and i not in [idx_jac, idx_cloud, idx_pareto, idx_bars]: ax_f[i].set_visible(False)
            
    is_dual = len(exp_names) == 2

    for idx, (name, exp_data) in enumerate(all_data.items()):
        color = HI_CONTRAST_COLORS[idx % len(HI_CONTRAST_COLORS)]
        short_name = short_names[idx]
        folds = exp_data["folds"]
        pool_x, pool_y = [], []
        line_handle, = ax_f[0].plot([], [], color=color, linewidth=3)
        legend_handles.append(line_handle); legend_labels.append(short_name)

        for f_idx in active_folds:
            if f_idx >= 5: continue
            if f_idx in folds:
                d = folds[f_idx]
                fx, fy = get_pareto_front(d["x"], d["y"])
                ax_f[f_idx].plot(fx, fy, color=color, alpha=1.0, linewidth=2)
                ax_f[f_idx].scatter(fx, fy, color=color, alpha=1.0, s=40, edgecolors='white', linewidths=0.5)
                pool_x.extend(d["x"]); pool_y.extend(d["y"])
                if len(d["y"])>0: 
                    y_min_g, y_max_g = min(y_min_g, np.min(d["y"])), max(y_max_g, np.max(d["y"]))
                    x_max_g = max(x_max_g, np.max(d["x"]))
                if is_dual:
                    other_d = all_data[exp_names[1-idx]]["folds"].get(f_idx)
                    if other_d: c_scores[name][f_idx] = calculate_c_metric(d["x"], d["y"], other_d["x"], other_d["y"])

        jk, jv = exp_data["jaccard"]["k"], exp_data["jaccard"]["v"]
        if jk: ax_f[idx_jac].plot(jk, jv, color=color, linewidth=2.5)
        ax_f[idx_cloud].scatter(pool_x, pool_y, color=color, alpha=0.3, s=20)
        gx, gy = get_pareto_front(np.array(pool_x), np.array(pool_y))
        ax_f[idx_pareto].plot(gx, gy, color=color, linewidth=3, marker='o', markersize=6)

    for i, ax in enumerate(ax_f):
        if i not in [idx_jac, idx_bars] and ax.get_visible():
            ax.set_box_aspect(1); ax.grid(True, linestyle=':', alpha=0.6)
        if i in active_folds:
            ax.set_ylim(max(0, y_min_g-0.05), min(1.0, y_max_g+0.05)); ax.set_xlim(-1, x_max_g+2)
            title = f"Fold {i}"
            if is_dual: title += f"\nC(A,B):{c_scores[exp_names[0]].get(i, 0):.2f} | C(B,A):{c_scores[exp_names[1]].get(i, 0):.2f}"
            ax.set_title(title, fontsize=10); ax.set_ylabel("Balanced Accuracy")
        elif i == idx_cloud:
            ax.set_ylim(max(0, y_min_g-0.05), min(1.0, y_max_g+0.05)); ax.set_xlim(-1, x_max_g+2)
            title = "Nube Agregada"
            if is_dual:
                m_ab = np.mean(list(c_scores[exp_names[0]].values())) if c_scores[exp_names[0]] else 0
                m_ba = np.mean(list(c_scores[exp_names[1]].values())) if c_scores[exp_names[1]] else 0
                title += f"\nMean C(A,B):{m_ab:.2f} | Mean C(B,A):{m_ba:.2f}"
            ax.set_title(title, fontweight='bold'); ax.set_ylabel("Balanced Accuracy"); ax.set_xlabel("Nº Genes")
        elif i == idx_pareto:
            ax.set_ylim(max(0, y_min_g-0.05), min(1.0, y_max_g+0.05)); ax.set_xlim(-1, x_max_g+2)
            title = "Frontera Pareto Global"
            if is_dual:
                x1, y1 = [x for f in all_data[exp_names[0]]["folds"].values() for x in f.get("x", [])], [y for f in all_data[exp_names[0]]["folds"].values() for y in f.get("y", [])]
                x2, y2 = [x for f in all_data[exp_names[1]]["folds"].values() for x in f.get("x", [])], [y for f in all_data[exp_names[1]]["folds"].values() for y in f.get("y", [])]
                cg_ab = calculate_c_metric(np.array(x1), np.array(y1), np.array(x2), np.array(y2)) if x1 and x2 else 0.0
                cg_ba = calculate_c_metric(np.array(x2), np.array(y2), np.array(x1), np.array(y1)) if x1 and x2 else 0.0
                title += f"\nGlobal C(A,B): {cg_ab:.2f} | C(B,A): {cg_ba:.2f}"
            ax.set_title(title, fontweight='bold', color='darkgreen'); ax.set_xlabel("Nº Genes")

    ax_j = ax_f[idx_jac]
    ax_j.set_box_aspect(1); ax_j.grid(True, linestyle=':', alpha=0.6)
    ax_j.set_title("Estabilidad Inter-fold (Jaccard)", fontweight='bold')
    ax_j.set_xlabel("Top K Features"); ax_j.set_ylabel("Stability Score")
    ax_j.autoscale(enable=True, axis='y', tight=False)

    ax_b = ax_f[idx_bars]
    ax_b.set_box_aspect(1); ax_b2 = ax_b.twinx(); ax_b2.set_box_aspect(1)
    
    n_exps, total_width = len(exp_names), 0.8
    width, x_pos = total_width / n_exps, np.arange(2)
    for idx, (name, exp_data) in enumerate(all_data.items()):
        color = HI_CONTRAST_COLORS[idx % len(HI_CONTRAST_COLORS)]
        offset = (idx - n_exps/2 + 0.5) * width
        m = exp_data["metrics"]
        ax_b.bar(x_pos[0] + offset, m["chv_m"], width, yerr=m["chv_s"], capsize=3, color=color, alpha=0.9, edgecolor='black')
        if m.get("schv_m", 0) > 0:
            ax_b.bar(x_pos[0] + offset, m["schv_m"], width, color=color, alpha=0.25, edgecolor=color, hatch='///', linewidth=1)
        ax_b2.bar(x_pos[1] + offset, m["var_m"], width, yerr=m["var_s"], capsize=3, color=color, alpha=0.9, edgecolor='black', hatch='//')
        
    ax_b.set_xticks(x_pos); ax_b.set_xticklabels(['Cross Hypervolume\n(Sólido=Std, Rayado=Soft)', 'Variety (Jaccard)'], fontweight='bold')
    ax_b.set_ylabel('Cross Hypervolume'); ax_b2.set_ylabel('Variety Score (Lower is Better)')
    ax_b.set_title('Métricas Oficiales MONOMER', fontweight='bold')

    fig.legend(handles=legend_handles, labels=legend_labels, loc='lower center', ncol=min(4, len(exp_names)), bbox_to_anchor=(0.5, 0.02), frameon=True, fontsize=12)
    title_comp = comp_name.replace('_vs_', ' VS ') if is_dual else f"Comparativa Múltiple ({len(exp_names)} variantes)"
    fig.suptitle(f"BENCHMARK {dataset_name.upper()} | {title_comp}", fontsize=20, fontweight='bold', y=0.98 if is_small_test else 0.95)
    plt.subplots_adjust(hspace=0.6, wspace=0.35)
    
    timestamp_str = datetime.now().strftime("%d%m_%H%M%S")
    final_img_name = f"bench_{len(exp_names)}algos_{timestamp_str}.png"
    plt.savefig(os.path.join(output_subdir, final_img_name), dpi=300, bbox_inches='tight')
    plt.close()

# --- LÓGICA DE NAVEGACIÓN Y CLI FAST ---

def list_dirs(path, restrict=False):
    try:
        items = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')])
        if restrict: return [d for d in items if d in ALLOWED_DATASETS]
        return items
    except: return []

def run_fast_plot(nicks, pop, gen, inner_folds):
    """Ejecuta el ploteo directo buscando las carpetas exactas."""
    console.print(f"\n[bold green]=== MODO FAST PLOT ACTIVADO ===[/bold green]")
    console.print(f"[cyan]Nicks a buscar:[/cyan] {nicks}")
    console.print(f"[cyan]Escala de Búsqueda NSGA:[/cyan] Pop={pop}, Gen={gen}, InnerFolds={inner_folds}\n")
    
    timestamp_str = datetime.now().strftime("%d%m_%H%M")
    out_base = os.path.join(BASE_OUTPUT_DIR, f"Fast_Plot_{timestamp_str}")
    
    outer_dir = "5_folds" if pop >= 100 else "2_folds"
    
    for dataset, mapping in FAST_MODE_MAPPING.items():
        model = mapping["best_model"]
        base_algo = mapping["best_algo"]
        obj_dir = {"naive_bayes": "NB_bal_acc_leanness", "RF": "RF_bal_acc_leanness", "svm": "leanness_svm_bal_acc"}.get(model)
        
        exp_base = os.path.join(WORK_DIR, dataset, "mrna", obj_dir, outer_dir)
        
        if not os.path.exists(exp_base):
            console.print(f"[yellow][-] Saltando {dataset} (Ruta {exp_base} no existe)[/yellow]")
            continue
            
        available_folders = list_dirs(exp_base)
        selected_paths = {}
        
        expected_nsga = get_expected_nsga_name(base_algo, pop, gen, inner_folds)
        if expected_nsga in available_folders:
            selected_paths[expected_nsga] = os.path.join(exp_base, expected_nsga)
        else:
            console.print(f"  [yellow]Advertencia: No se encontró el baseline {expected_nsga}[/yellow]")
            
        for nick in nicks:
            found = False
            # NUEVA BUSQUEDA AGNOSTICA DEL SUFIJO (Soporta (none,none), (MV_lassoFI,none), etc.)
            pattern = re.compile(rf"^moabc_.*_{re.escape(nick)}_\(.*\)$", re.IGNORECASE)
            
            for folder in available_folders:
                if pattern.match(folder):
                    selected_paths[folder] = os.path.join(exp_base, folder)
                    found = True
                    break
            
            if not found:
                console.print(f"  [red]Falta: {nick} en {dataset}[/red]")
                
        if len(selected_paths) < 2:
            console.print(f"[yellow][-] Saltando {dataset} (No hay suficientes experimentos para comparar)[/yellow]")
            continue
            
        comp_name = f"Fast_{dataset}_{model}"
        out_dir = os.path.join(out_base, dataset)
        
        console.print(f"[*] Ploteando [bold]{dataset.upper()}[/bold] con {len(selected_paths)} algoritmos...")
        plot_comparison(selected_paths, out_dir, dataset, comp_name)
        
    console.print(f"\n[bold green]¡Fast Plot completado! Resultados en: {out_base}[/bold green]")

def render_menu(options, title):
    table = Table(title=title, box=box.HEAVY_EDGE, header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Nombre")
    for i, o in enumerate(options): table.add_row(str(i+1), o)
    table.add_row("0", "SALIR / ATRÁS")
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Plotter Interactivo & Fast Mode")
    parser.add_argument('--fast_plot', nargs='*', help="Lanza el modo directo buscando estos nicks")
    parser.add_argument('--pop', type=int, default=200, help="Población usada para encontrar NSGA")
    parser.add_argument('--gen', type=int, default=250, help="Generaciones usadas para encontrar NSGA")
    parser.add_argument('--inner_folds', type=int, default=3, help="Inner Folds para encontrar NSGA")
    args = parser.parse_args()
    
    if args.fast_plot is not None:
        run_fast_plot(args.fast_plot, args.pop, args.gen, args.inner_folds)
        return

    # Modo Interactivo
    state = 0
    sel_dataset = sel_view = sel_model = sel_schema = None

    while True:
        console.clear()
        console.print(Panel.fit(" MONOMER - Interactive Benchmarker ", border_style="blue"))

        if state == 0:
            opts = list_dirs(WORK_DIR, True)
            render_menu(opts, "1. Selecciona DATASET")
            raw = Prompt.ask("ID")
            if raw == "0": break
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                sel_dataset = opts[int(raw)-1]
                state = 1
        
        elif state == 1:
            opts = list_dirs(os.path.join(WORK_DIR, sel_dataset))
            render_menu(opts, f"2. VISTA (Dataset: {sel_dataset})")
            raw = Prompt.ask("ID")
            if raw == "0": state = 0; continue
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                sel_view = opts[int(raw)-1]
                state = 2

        elif state == 2:
            opts = list_dirs(os.path.join(WORK_DIR, sel_dataset, sel_view))
            render_menu(opts, f"3. MODELO (Vista: {sel_view})")
            raw = Prompt.ask("ID")
            if raw == "0": state = 1; continue
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                sel_model = opts[int(raw)-1]
                state = 3

        elif state == 3:
            opts = list_dirs(os.path.join(WORK_DIR, sel_dataset, sel_view, sel_model))
            render_menu(opts, f"4. ESQUEMA DE FOLDS (Modelo: {sel_model})")
            raw = Prompt.ask("ID")
            if raw == "0": state = 2; continue
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                sel_schema = opts[int(raw)-1]
                state = 4

        elif state == 4:
            exp_base = os.path.join(WORK_DIR, sel_dataset, sel_view, sel_model, sel_schema)
            opts = list_dirs(exp_base)
            render_menu(opts, "5. EXPERIMENTOS A COMPARAR (ej: 1,2 o 1,2,4,5)")
            raw = Prompt.ask("IDs (separados por coma)")
            if raw == "0": state = 3; continue
            
            try:
                indices = [int(i.strip()) - 1 for i in raw.split(",") if i.strip().isdigit()]
                selected = [opts[i] for i in indices if 0 <= i < len(opts)]
                if len(selected) < 2:
                    console.print("\n[yellow]Selecciona al menos 2 experimentos.[/yellow]")
                    Prompt.ask("Presiona Enter para continuar")
                    continue
                
                short_names = [shorten_exp_name(n) for n in selected]
                timestamp_str = datetime.now().strftime("%d%m_%H%M%S")
                comp_name = f"{short_names[0]}_vs_{short_names[1]}" if len(selected) == 2 else f"Comparativa_{len(selected)}_algoritmos"
                out_dir = os.path.join(BASE_OUTPUT_DIR, sel_dataset, sel_model, f"{comp_name}_{timestamp_str}")

                with console.status(f"[bold green]Calculando métricas para {len(selected)} experimentos..."):
                    plot_comparison(selected_paths, out_dir, dataset, comp_name)
                    
                console.print(f"\n[bold green]¡Éxito! Gráfica guardada en:[/bold green] [cyan]{out_dir}[/cyan]")
                Prompt.ask("\nPresiona Enter para seguir graficando o 0 para salir")
            except Exception as e:
                console.print(f"\n[bold red]Error durante el ploteo: {e}[/bold red]")
                Prompt.ask("Presiona Enter para continuar")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Proceso cancelado.[/red]")