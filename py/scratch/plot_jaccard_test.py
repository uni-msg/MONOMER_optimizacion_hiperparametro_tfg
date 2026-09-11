import os
import sys
import glob
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Headless para SSH
import matplotlib.pyplot as plt

# --- IMPORTACIONES DEL FRAMEWORK ORIGINAL ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'py')))
try:
    from util.list_math import mean_all_vs_others, jaccard
    from util.components_transform import HigherKComponents
    from util.sequence_utils import to_common_labels
except ImportError as e:
    print(f"Error importando módulos del framework: {e}")
    sys.exit(1)

COLORS = ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3']

def calculate_temporal_jaccard(jsonl_files):
    """
    Lee los JSONL (formato lista plana), sincroniza por generación, 
    y calcula el Jaccard medio y su dispersión.
    """
    gen_data = {}
    
    for filepath in jsonl_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        data = json.loads(line)
                        g = data.get('gen', 0)
                        evals = data.get('evals', 0)
                        front = data.get('front', [])
                        
                        # Nuevo formato ultraligero: front es una lista de listas [f0, f1, [genes]]
                        if not front or len(front[0]) < 3:
                            continue
                            
                        # Extraer todos los genes activos en el frente Pareto actual
                        fold_genes = []
                        for ind in front:
                            fold_genes.extend(ind[2]) # El índice 2 contiene la lista de genes
                        
                        if g not in gen_data:
                            gen_data[g] = {'evals': [], 'folds_genes': []}
                        
                        gen_data[g]['evals'].append(evals)
                        gen_data[g]['folds_genes'].append(pd.Series(fold_genes).value_counts())
                        
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error leyendo {filepath}: {e}")
            
    sorted_gens = sorted(gen_data.keys())
    x_evals, y_mean, y_std = [], [], []
    
    for g in sorted_gens:
        folds_series = gen_data[g]['folds_genes']
        
        if len(folds_series) < 2:
            continue
            
        aligned = to_common_labels(folds_series)
        fold_counts = [pd.Series(li).fillna(0).tolist() for li in aligned]
        
        max_k = min([sum([a != 0 for a in fc]) for fc in fold_counts])
        if max_k <= 0:
            continue
            
        j_vals_for_gen = []
        for k in range(1, max_k + 1):
            comp = HigherKComponents(k)
            fold_counts_k = [comp.apply(c) for c in fold_counts]
            j_vals_for_gen.append(mean_all_vs_others(fold_counts_k, jaccard))
            
        if j_vals_for_gen:
            x_evals.append(np.mean(gen_data[g]['evals'])) 
            y_mean.append(np.mean(j_vals_for_gen))       
            y_std.append(np.std(j_vals_for_gen))         
            
    return np.array(x_evals), np.array(y_mean), np.array(y_std)

def plot_jaccard_evolution():
    base_dir = os.getcwd() 
    
    experiment_paths = [
        "brca/mrna/leanness_svm_bal_acc/5_folds/moabc_p200_ev50000_dE70_dO80_L10_cascade_17_(none,none)",
        "brca/mrna/leanness_svm_bal_acc/5_folds/moabc_p500_ev500000_dE70_dO80_L10_cascade_17_(none,none)",
        ]
    
    plt.figure(figsize=(14, 8))
    plotted_lines = 0
    
    print("\n" + "=" * 65)
    print(" ANÁLISIS DE CONVERGENCIA DE ESTABILIDAD (JACCARD)")
    print("=" * 65)
    
    for idx, rel_path in enumerate(experiment_paths):
        full_path = os.path.join(base_dir, rel_path)
        
        dataset_name = rel_path.split('/')[0].upper()
        classifier = 'NB' if 'NB' in rel_path else 'RF' if 'RF' in rel_path else 'SVM'
        label = f"{dataset_name} ({classifier})"
        color = COLORS[idx % len(COLORS)]
        
        search_pattern = os.path.join(full_path, "**", "front_snapshots_fold_*.jsonl")
        jsonl_files = glob.glob(search_pattern, recursive=True)
        
        if not jsonl_files: continue
            
        print(f"[+] Procesando {label} (Leyendo {len(jsonl_files)} folds...)")
        x_evals, y_mean, y_std = calculate_temporal_jaccard(jsonl_files)
        
        if len(x_evals) > 0:
            window = max(1, len(y_mean) // 20)
            y_mean_smooth = pd.Series(y_mean).rolling(window=window, min_periods=1).mean()
            y_std_smooth = pd.Series(y_std).rolling(window=window, min_periods=1).mean()
            
            plt.plot(x_evals, y_mean_smooth, label=label, color=color, linewidth=2.5, alpha=0.9)
            plt.plot(x_evals, y_mean_smooth + y_std_smooth, color=color, linestyle=':', alpha=0.7, linewidth=1.5)
            plt.plot(x_evals, y_mean_smooth - y_std_smooth, color=color, linestyle=':', alpha=0.7, linewidth=1.5)
            plt.fill_between(x_evals, y_mean_smooth - y_std_smooth, y_mean_smooth + y_std_smooth, color=color, alpha=0.1)
            
            plotted_lines += 1
        else:
            print(f"[-] Advertencia: Sin datos válidos para {dataset_name}.")

    if plotted_lines > 0:
        plt.title("Evolución Temporal de la Inestabilidad (Jaccard) - Menor es Mejor", fontsize=16, fontweight='bold')
        plt.xlabel("Evaluaciones Consumidas", fontsize=14)
        plt.ylabel("Mean Jaccard Score (Menor = Más Estable)", fontsize=14)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend(fontsize=12, loc="upper right")
        
        out_file = os.path.join(base_dir, "jaccard_convergence_test.png")
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        print("-" * 65)
        print(f"[ÉXITO] Gráfica generada y guardada en: {out_file}\n")
    else:
        print("\n[ERROR] No se pudo generar la gráfica.")

if __name__ == "__main__":
    plot_jaccard_evolution()