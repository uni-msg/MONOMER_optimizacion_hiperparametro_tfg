import os
import sys
import glob
import json
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.ticker as ticker # Necesario para el ajuste de ticks
matplotlib.use('Agg') # Headless para SSH
import matplotlib.pyplot as plt
import re
import ast # Para evaluar la lista de Jaccard

# --- Importes para Cálculo Offline de Hipervolumen ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'py')))
from util.hyperbox.hyperbox import ConcreteHyperbox0B
from util.cross_hypervolume.cross_hypervolume import hypervolume

# Paleta de colores de alto contraste
COLORS = ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3']

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
                data = json.loads(line)
                evals.append(data.get('evals', 0))
                hvs.append(calculate_offline_hypervolume(data.get('front', [])))
            except json.JSONDecodeError: continue
    return pd.DataFrame({'evaluations': evals, 'inner_hypervolume': hvs})

# Las funciones find_knee_point y find_plateau_point ya estaban bien.

def find_knee_point(evals, hvs):
    """Cota Inferior: Detección del Codo (Máxima Eficiencia)"""
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
    """Cota Superior de Seguridad: Alcanzar el X% del máximo absoluto"""
    hvs_smooth = pd.Series(hvs).rolling(window=5, min_periods=1).mean().values
    max_hv = np.max(hvs_smooth)
    target_hv = max_hv * threshold
    
    # Encontrar el primer índice donde se supera el threshold
    plateau_idx = np.argmax(hvs_smooth >= target_hv)
    return evals[plateau_idx], hvs[plateau_idx]


def plot_preliminary_convergence():
    base_dir = os.getcwd() 
    experiment_paths = [
        "brca/mrna/leanness_svm_bal_acc/5_folds/moabc_p200_ev50000_dE70_dO80_L10_cascade_17_(none,none)",
        "brca/mrna/leanness_svm_bal_acc/5_folds/moabc_p500_ev500000_dE70_dO80_L10_cascade_17_(none,none)",
    ]
    
    plt.figure(figsize=(14, 8))
    plotted_lines = 0
    
    print("\n" + "=" * 80)
    print(" ANÁLISIS METODOLÓGICO DE CONVERGENCIA (CODO vs MESETA DE SEGURIDAD)")
    print("=" * 80)
    
    for idx, rel_path in enumerate(experiment_paths):
        full_path = os.path.join(base_dir, rel_path)
        
        dataset_name = rel_path.split('/')[0].upper()
        if 'NB' in rel_path: classifier = 'NB'
        elif 'RF' in rel_path: classifier = 'RF'
        else: classifier = 'SVM'
            
        label = f"{dataset_name} ({classifier})"
        color = COLORS[idx % len(COLORS)]
        
        search_pattern = os.path.join(full_path, "**", "front_snapshots_fold_*.jsonl")
        jsonl_files = glob.glob(search_pattern, recursive=True)
        
        if not jsonl_files: continue
            
        fold_dfs = []
        for f_path in jsonl_files:
            try:
                df = read_jsonl_log(f_path)
                if not df.empty: fold_dfs.append(df)
            except Exception: pass
                
        if not fold_dfs: continue
        
        base_evals = fold_dfs[0]['evaluations'].values
        valid_hvs = []
        
        for df in fold_dfs:
            if len(df) == len(base_evals) and np.array_equal(df['evaluations'].values, base_evals):
                valid_hvs.append(df['inner_hypervolume'].values)
            elif len(df) > 0:
                valid_hvs.append(np.interp(base_evals, df['evaluations'].values, df['inner_hypervolume'].values))
                
        if valid_hvs:
            avg_hv = np.mean(valid_hvs, axis=0)
            
            # --- CÁLCULOS MATEMÁTICOS ---
            knee_eval, knee_hv = find_knee_point(base_evals, avg_hv)
            plateau_eval, plateau_hv = find_plateau_point(base_evals, avg_hv, threshold=0.98)
            
            print(f"[+] {label:18}")
            print(f"    ├─ Codo (Mínimo eficiente) : {int(knee_eval):>8,} evals")
            print(f"    └─ Cota 98% (Presupuesto)  : {int(plateau_eval):>8,} evals\n")
            
            # --- GRAFICADO ---
            # Línea principal
            plt.plot(base_evals, avg_hv, label=f"{label} (Safe: {int(plateau_eval//1000)}k)", color=color, linewidth=2.5, alpha=0.85)
            
            # Marcador 1: Estrella en el Codo (Eficiencia)
            plt.scatter(knee_eval, knee_hv, marker='*', s=200, color=color, edgecolor='black', zorder=5)
            
            # Marcador 2: Círculo y línea vertical en la Meseta (Seguridad)
            plt.scatter(plateau_eval, plateau_hv, marker='o', s=100, color=color, edgecolor='white', zorder=6)
            plt.axvline(x=plateau_eval, color=color, linestyle='--', alpha=0.4)
            
            plotted_lines += 1

    if plotted_lines > 0:
        plt.title("Análisis de Convergencia: Detección de Codo (*) vs Cota de Seguridad 98% (o)", fontsize=16, fontweight='bold')
        plt.xlabel("Evaluaciones Consumidas", fontsize=14)
        plt.ylabel("Mean Inner CV Hypervolume (5 Folds)", fontsize=14)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend(fontsize=12, loc="lower right")
        
        out_file = os.path.join(base_dir, "preliminary_convergence_test.png")
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        print("=" * 80)
        print(f"[ÉXITO] Gráfica metodológica guardada en: {out_file}\n")

if __name__ == "__main__":
    plot_preliminary_convergence()