import os
import sys
import glob
import json
import configparser
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.ticker as ticker
matplotlib.use('Agg') # Headless para SSH
import matplotlib.pyplot as plt
import re
import ast
import importlib.util

# --- Importes para Cálculo Offline de Hipervolumen ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'py')))
from util.hyperbox.hyperbox import ConcreteHyperbox0B
from util.cross_hypervolume.cross_hypervolume import hypervolume

COLORS = [
    '#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#A65628', 
    '#F781BF', '#999999', '#17BECF', '#BCBD22', '#8C564B', '#1f77b4',
    '#2ca02c', '#d62728', '#9467bd', '#8c564b'
]
TARGET_DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]

def calculate_offline_hypervolume(front_coordinates):
    if not front_coordinates: return 0.0
    hyperboxes = [ConcreteHyperbox0B.create_by_b_vals((p[0], p[1]) if isinstance(p, list) else (p['f0'], p['f1'])) for p in front_coordinates]
    return hypervolume(hyperboxes)

def read_jsonl_log(filepath):
    evals, hvs = [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                data = json.loads(line); evals.append(data.get('evals', 0))
                hvs.append(calculate_offline_hypervolume(data.get('front', [])))
            except: continue
    return pd.DataFrame({'evaluations': evals, 'inner_hypervolume': hvs})

def extract_metrics_from_log(log_path):
    """Extrae métricas exclusivamente del bloque PARETO FRONT (Alineado con Cattelani)."""
    if not os.path.exists(log_path): return None, None, None, None
    cross_hv_list = []
    mean_jaccard, std_jaccard = None, None
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        parts = content.split("EVALUATING HALL OF FAME PARETO FRONT")
        if len(parts) >= 2:
            pareto_block = parts[1].split("EVALUATING HALL OF FAME BEST SUMS")[0]
            hv_matches = re.findall(r'Cross hypervolume:\s*([0-9]*\.?[0-9]+)', pareto_block)
            if hv_matches:
                cross_hv_list = [float(m) for m in hv_matches[:5]]
                
            jac_array_match = re.search(r'Mean Jaccard all vs others for each fold\s*(\[.*?\])', pareto_block, re.DOTALL)
            if jac_array_match:
                jac_list = ast.literal_eval(jac_array_match.group(1))
                mean_jaccard, std_jaccard = np.mean(jac_list), np.std(jac_list)
                
    if not cross_hv_list or mean_jaccard is None: return None, None, None, None
    return np.mean(cross_hv_list), np.std(cross_hv_list), mean_jaccard, std_jaccard

def find_knee_point(evals, hvs):
    hvs_smooth = pd.Series(hvs).rolling(window=5, min_periods=1).mean().values
    e_min, e_max = np.min(evals), np.max(evals)
    h_min, h_max = np.min(hvs_smooth), np.max(hvs_smooth)
    if h_max == h_min or e_max == e_min: return evals[-1], hvs[-1]
    evals_norm = (evals - e_min) / (e_max - e_min)
    hvs_norm = (hvs_smooth - h_min) / (h_max - h_min)
    distances = hvs_norm - evals_norm
    knee_idx = np.argmax(distances)
    return evals[knee_idx], hvs[knee_idx]

def find_plateau_point(evals, hvs, threshold=0.98):
    hvs_smooth = pd.Series(hvs).rolling(window=5, min_periods=1).mean().values
    max_hv = np.max(hvs_smooth)
    target_hv = max_hv * threshold
    plateau_idx = np.argmax(hvs_smooth >= target_hv)
    return evals[plateau_idx], hvs[plateau_idx]

def sort_labels_key(label):
    numbers = [float(n) for n in re.findall(r'\d+\.?\d*', label)]
    return tuple(numbers) if numbers else (label,)

def load_cascade_config(base_dir):
    """Carga dinámicamente las variables configuradas en cascade_runner.py"""
    runner_path = os.path.join(base_dir, '..', 'py', 'cascade_runner.py')
    if not os.path.exists(runner_path):
        print(f"[!] No se encuentra {runner_path}")
        return None, None
    
    spec = importlib.util.spec_from_file_location("cascade_runner", runner_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cascade_runner"] = module
    try:
        spec.loader.exec_module(module)
        return getattr(module, 'FIXED_PARAMS', {}), getattr(module, 'EXPERIMENTS_TO_RUN', [])
    except Exception as e:
        print(f"[!] Error cargando cascade_runner.py: {e}")
        return None, None

def plot_live_monitor(mission_name, target_params, base_dir):
    print(f"\n{'='*70}\n LIVE MONITOR OMNISCIENTE: {mission_name.upper()}\n{'='*70}")
    
    report_dir = os.path.join(base_dir, "tuning_reports", mission_name)
    os.makedirs(report_dir, exist_ok=True)
    
    fixed_params, exp_to_run = load_cascade_config(base_dir)
    if not fixed_params or not exp_to_run: sys.exit(0)

    unique_labels = set()
    global_nicks = {} 
    
    for exp in exp_to_run:
        merged = fixed_params.copy()
        for k, v in exp.items():
            if k != "exp_id": merged[k] = v
            
        pop = merged.get("pop", "500")
        limit = merged.get("limit", "50")
        dE = int(float(merged.get("moabc_p_diversity_emp", "0.80")) * 100)
        dO = int(float(merged.get("moabc_p_diversity_obs", "0.80")) * 100)
        del_p = int(float(merged.get("moabc_p_local_del", "0.25")) * 100)
        ls = merged.get("moabc_scout_ls_genes", "3")
        
        nick = f"moabc_std_p{pop}_L{limit}_dE{dE}_dO{dO}_del{del_p}_ls{ls}_(none,none)"
        
        label_parts = []
        for p in target_params:
            val = merged.get(p, "?")
            if p == "limit": label_parts.append(f"L{val}")
            elif "ls_genes" in p: label_parts.append(f"S{val}")
            elif "diversity_emp" in p: label_parts.append(f"dE{val}")
            elif "diversity_obs" in p: label_parts.append(f"dO{val}")
            else: label_parts.append(f"{p}:{val}")
        
        label = "_".join(label_parts)
        unique_labels.add(label)
        global_nicks[label] = nick

    sorted_labels = sorted(list(unique_labels), key=sort_labels_key)
    COLOR_MAP = {l: COLORS[i % len(COLORS)] for i, l in enumerate(sorted_labels)}

    # =========================================================
    # 1. GRID 2x2 (CONVERGENCIA EN VIVO)
    # =========================================================
    fig, axes = plt.subplots(2, 2, figsize=(22, 16))
    axes = axes.flatten(); global_metrics = []
    
    for ax_idx, ds in enumerate(TARGET_DATASETS):
        ax = axes[ax_idx]; ax.set_title(f"Dataset: {ds.upper()}", fontweight='bold')
        plotted_in_ax = False
        print(f"\n[+] Buscando datos para {ds.upper()}...")
        
        for label in sorted_labels:
            nick = global_nicks[label]
            search_pattern = os.path.join(base_dir, ds, "mrna", "*", "5_folds", nick)
            matched_dirs = glob.glob(search_pattern)
            if not matched_dirs: continue
                
            target_dir = matched_dirs[0]
            jsonl_files = glob.glob(os.path.join(target_dir, "front_snapshots_fold_*.jsonl"))
            if not jsonl_files: continue
            
            fold_dfs = [read_jsonl_log(f) for f in jsonl_files if not read_jsonl_log(f).empty]
            if fold_dfs:
                base_evals = fold_dfs[0]['evaluations'].values
                valid_hvs = [np.interp(base_evals, df['evaluations'].values, df['inner_hypervolume'].values) for df in fold_dfs]
                avg_hv = np.mean(valid_hvs, axis=0)
                color = COLOR_MAP[label]
                
                knee_e, knee_h = find_knee_point(base_evals, avg_hv)
                plat_e, plat_h = find_plateau_point(base_evals, avg_hv, 0.98)
                
                print(f"    ├─ {label:18} -> Codo: {int(knee_e):>7,} | 98%: {int(plat_e):>7,}")
                
                ax.plot(base_evals, avg_hv, label=f"{label} (Safe: {int(plat_e//1000)}k)", color=color, linewidth=2, alpha=0.8)
                ax.scatter(knee_e, knee_h, marker='*', s=120, color=color, edgecolor='black', zorder=5)
                ax.scatter(plat_e, plat_h, marker='o', s=60, color=color, edgecolor='white', zorder=6)
                
                plotted_in_ax = True
                
                # --- EXTRACCIÓN DE MÉTRICAS FINALES PARA EL SCATTER (ALINEADO) ---
                log_file = os.path.join(target_dir, "log.txt")
                if os.path.exists(log_file):
                    mean_hv, std_hv, mean_jac, std_jac = extract_metrics_from_log(log_file)
                    if mean_hv is not None and mean_jac is not None:
                        global_metrics.append({
                            "label": label,
                            "chv_m": mean_hv,
                            "chv_s": std_hv if std_hv is not None else 0.0,
                            "jac_m": mean_jac,
                            "jac_s": std_jac if std_jac is not None else 0.0
                        })

        if plotted_in_ax:
            ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=10)
            ax.grid(True, linestyle=':'); ax.set_xlabel("Evaluaciones"); ax.set_ylabel("Inner HV")
        else:
            ax.text(0.5, 0.5, "Esperando datos...", ha='center', va='center', transform=ax.transAxes, color='gray')

    plt.tight_layout()
    plt.savefig(os.path.join(report_dir, f"{mission_name}_live_grid.png"), dpi=300)
    plt.close()
    print(f"\n[+] Guardado Live Convergence Grid: {report_dir}")

    # =========================================================
    # 2. SCATTER PLOT EN VIVO (ISOTRÓPICO CON BIGOTES CROSS HV)
    # =========================================================
    if not global_metrics: print("\n[!] No hay logs finales terminados aún."); sys.exit(0)
    
    # numeric_only=True añadido para evitar el FutureWarning de Pandas
    df_s = pd.DataFrame(global_metrics).groupby('label').mean(numeric_only=True).reset_index()
    df_s['sort_key'] = df_s['label'].apply(sort_labels_key)
    df_s = df_s.sort_values('sort_key').drop('sort_key', axis=1)

    fig_sc, ax_sc = plt.subplots(figsize=(10, 10))
    x_m, y_m = df_s['jac_m'].values, df_s['chv_m'].values
    x_s, y_s = df_s['jac_s'].values, df_s['chv_s'].values

    for idx, row in df_s.iterrows():
        c = COLOR_MAP[row['label']]
        ax_sc.errorbar(row['jac_m'], row['chv_m'], xerr=row['jac_s'], yerr=row['chv_s'], fmt='none', ecolor=c, capsize=4, alpha=0.6, zorder=2)
        ax_sc.scatter(row['jac_m'], row['chv_m'], color=c, s=250, edgecolor='black', label=row['label'], zorder=3)

    xr, yr = np.ptp(x_m)+max(x_s)*2, np.ptp(y_m)+max(y_s)*2
    mx, my = (xr or 0.05)*0.05, (yr or 0.05)*0.05
    min_x, max_x = min(x_m-x_s)-mx, max(x_m+x_s)+mx
    min_y, max_y = min(y_m-y_s)-my, max(y_m+y_s)+my
    ax_sc.set_xlim(min_x, max_x); ax_sc.set_ylim(min_y, max_y)
    
    step = max(xr, yr) / 6.0
    exponent = np.floor(np.log10(step)) if step>0 else 0
    nice_step = (1 if (step/10**exponent)<=1.5 else 2 if (step/10**exponent)<=3.5 else 5) * 10**exponent
    ax_sc.xaxis.set_major_locator(ticker.MultipleLocator(nice_step))
    ax_sc.yaxis.set_major_locator(ticker.MultipleLocator(nice_step))
    ax_sc.set_aspect('equal', adjustable='box')

    ax_sc.set_title(f"Live Trade-off (Cross Hypervolume): {mission_name}", fontsize=14, fontweight='bold', pad=20)
    ax_sc.set_xlabel("Variedad (Mean Jaccard ± Std | ← Más Variedad)"); ax_sc.set_ylabel("Generalización (Mean Cross HV ± Std | ↑ Mejor)")
    ax_sc.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), title="Configs")
    ax_sc.grid(True, linestyle=':', alpha=0.5)
    
    ax_sc.text(min_x + mx, max_y - my, "ÓPTIMO\n(Alta Calidad, Alta Variedad)", color='green', fontweight='bold', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))
    
    out_file2 = os.path.join(report_dir, f"{mission_name}_live_tradeoff.png")
    plt.savefig(out_file2, dpi=300, bbox_inches='tight')
    print(f"[+] Gráficas actualizadas en {out_file2}")

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Uso: python plot_live_monitor.py <MISIÓN> <PARAMS...>"); sys.exit(1)
    plot_live_monitor(sys.argv[1], sys.argv[2:], os.getcwd())