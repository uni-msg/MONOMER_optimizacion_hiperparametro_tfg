import pandas as pd
import numpy as np
import sys
import os
import glob
from pathlib import Path

# --- FUNCIONES MATEMÁTICAS (Robustas y filtradas) ---

def get_pareto_front(data):
    """
    Filtra y devuelve solo los puntos no dominados (Frente Pareto real).
    Fundamental para comparar justamente en Test.
    """
    data = np.unique(data, axis=0)
    n_points = data.shape[0]
    if n_points == 0: return data

    is_pareto = np.ones(n_points, dtype=bool)
    for i in range(n_points):
        for j in range(n_points):
            if i == j: continue
            if all(data[j] >= data[i]) and any(data[j] > data[i]):
                is_pareto[i] = False
                break
    return data[is_pareto]

def calculate_c_metric(front_a, front_b):
    """Calcula C(A, B): % de B dominado por A."""
    if len(front_b) == 0: return 0.0
    dominated_count = 0
    for sol_b in front_b:
        is_better_eq = np.all(front_a >= sol_b, axis=1)
        is_strictly_better = np.any(front_a > sol_b, axis=1)
        if np.any(is_better_eq & is_strictly_better):
            dominated_count += 1
    return dominated_count / len(front_b)

def find_columns(df, phase):
    """Busca columnas de bal_acc y leanness tolerando formatos variados."""
    acc_col = None
    lean_col = None
    phase_prefix = phase.lower()
    for col in df.columns:
        c_lower = col.lower()
        if phase_prefix not in c_lower: continue
        if "bal_acc" in c_lower: acc_col = col
        elif "leanness" in c_lower: lean_col = col
    return acc_col, lean_col

# --- LÓGICA DE FICHEROS ---

def find_fold_files(base_path):
    """Busca recursivamente solution_fitnesses_fold_*.csv"""
    # Usamos glob recursivo con pathlib para compatibilidad
    search_path = Path(base_path)
    files = list(search_path.rglob("solution_fitnesses_fold_*.csv"))
    
    fold_map = {}
    for f in files:
        try:
            # Extraer número del fold del nombre de archivo
            # Formato esperado: ..._fold_X.csv
            fname = f.name
            fold_str = fname.split("_fold_")[-1].replace(".csv", "")
            fold_num = int(fold_str)
            fold_map[fold_num] = str(f)
        except ValueError:
            continue
    return fold_map

def compare_single_file_pair(file1, file2, phase):
    """Procesa un par de ficheros para una fase específica."""
    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        
        acc1, lean1 = find_columns(df1, phase)
        acc2, lean2 = find_columns(df2, phase)
        
        if not (acc1 and lean1 and acc2 and lean2):
            return None, None # Columnas no encontradas

        raw1 = df1[[acc1, lean1]].dropna().values
        raw2 = df2[[acc2, lean2]].dropna().values
        
        # FILTRADO PARETO (Crucial)
        front1 = get_pareto_front(raw1)
        front2 = get_pareto_front(raw2)
        
        c_ab = calculate_c_metric(front1, front2)
        c_ba = calculate_c_metric(front2, front1)
        
        return c_ab, c_ba
    except Exception:
        return None, None

# --- PROGRAMA PRINCIPAL ---

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 compare_algorithms_full.py <carpeta_A> <carpeta_B>")
        return

    dir_a = sys.argv[1]
    dir_b = sys.argv[2]

    print("\n" + "="*70)
    print(f"COMPARACIÓN MULTI-OBJETIVO COMPLETA (Set Coverage)")
    print(f"Algoritmo A: {dir_a}")
    print(f"Algoritmo B: {dir_b}")
    print("="*70)

    # 1. Mapear ficheros
    folds_a = find_fold_files(dir_a)
    folds_b = find_fold_files(dir_b)
    common_folds = sorted(list(set(folds_a.keys()) & set(folds_b.keys())))

    if not common_folds:
        print("ERROR: No se han encontrado folds comunes en ambas rutas.")
        return

    # 2. Iterar por fases
    phases = ["inner_cv", "train", "test"]
    
    for phase in phases:
        print(f"\n>>> FASE: {phase.upper()}")
        print(f"{'FOLD':<6} | {'C(A, B)':<10} | {'C(B, A)':<10} | {'GANADOR':<10}")
        print("-" * 50)
        
        scores_ab = []
        scores_ba = []
        
        for fold in common_folds:
            c_ab, c_ba = compare_single_file_pair(folds_a[fold], folds_b[fold], phase)
            
            if c_ab is None:
                print(f"{fold:<6} | {'---':<10} | {'---':<10} | (No data)")
                continue
                
            scores_ab.append(c_ab)
            scores_ba.append(c_ba)
            
            winner = "A" if c_ab > c_ba else "B" if c_ba > c_ab else "="
            print(f"{fold:<6} | {c_ab:<10.4f} | {c_ba:<10.4f} | {winner}")

        # Resumen de la fase
        if scores_ab:
            avg_ab = np.mean(scores_ab)
            avg_ba = np.mean(scores_ba)
            print("-" * 50)
            print(f"MEDIA  | {avg_ab:<10.4f} | {avg_ba:<10.4f} |")
            
            diff = avg_ab - avg_ba
            if diff > 0:
                print(f">> En {phase.upper()}, A gana por un margen medio de {diff:.4f}")
            elif diff < 0:
                print(f">> En {phase.upper()}, B gana por un margen medio de {-diff:.4f}")
            else:
                print(f">> Empate técnico en {phase.upper()}")
        else:
            print(f">> No se encontraron datos válidos para la fase {phase.upper()}")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()