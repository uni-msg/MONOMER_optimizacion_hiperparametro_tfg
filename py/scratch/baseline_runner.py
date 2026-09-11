# --- START OF FILE baseline_runner.py ---

import os
import sys
import subprocess
import configparser
import numpy as np
import glob
import pandas as pd
import json
import argparse
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'py')))

try:
    from util.hyperbox.hyperbox import ConcreteHyperbox0B
    from util.cross_hypervolume.cross_hypervolume import cross_hypervolume
    from saved_solutions.run_fold_jaccard import compute_jaccard_from_lists
except ImportError:
    print("[!] Advertencia: No se pudieron importar las librerías de métricas de Cattelani.")

# =====================================================================
# 1. CONFIGURACIÓN Y MAPEOS GENERALES
# =====================================================================

ALL_DATASETS = ["brca", "luad_lusc", "tcga_kir", "tcga_ov"]
ALL_MODELS = ["svm", "naive_bayes", "RF"]

MOABC_BASE = {
    "views_to_use": '["mrna"]',
    "mvmo_algorithm": "abc_mo",
    "feature_importance_survival": "none",
    "cross_validation": "true",
    "final_optimization": "false",
    "sorting_strategy": "crowding_distance_clone_index",
    "use_clone_repurposing": "true",
    "external_dataset": "swedish",
    "logistic_max_iter": "100",
    "limit": "10",
    "moabc_p_watering_emp": "0.70",     
    "moabc_p_prune_obs": "0.70",
    "moabc_p_guided_add": "0.60",
    "moabc_p_guided_del": "0.30",       
    "moabc_enable_stratified_init": "false",
    "moabc_init_min_size": "3",
    "moabc_init_max_size": "80",
    "moabc_enable_leader_proximity": "false",
    "moabc_leader_tournament_size": "2",
    "moabc_enable_crowding_onlookers": "false",
    "moabc_enable_reactive_watering": "false",
    "moabc_stag_threshold": "10",
    "moabc_stag_fraction": "0.20",
    "moabc_enable_levy_scout": "false",
    "moabc_levy_beta": "1.5",
    "moabc_levy_scale": "3.0",
    "moabc_enable_pure_employed": "false"
}

MOABC_LASSO = MOABC_BASE.copy()
MOABC_LASSO["feature_importance_categorical"] = "lasso"

MOABC_UNIFORM = MOABC_BASE.copy()
MOABC_UNIFORM["feature_importance_categorical"] = "none"

NSGA2_PARAMS = {
    "mvmo_algorithm": "classic_ga",
    "sorting_strategy": "crowding_distance_full",
    "external_dataset": "swedish",
    "cross_validation": "true",
    "final_optimization": "false"
}

NSGA2_CH_PARAMS = {
    "mvmo_algorithm": "classic_ga",
    "feature_importance_categorical": "lasso",
    "sorting_strategy": "crowding_distance_clone_index",
    "external_dataset": "swedish",
    "cross_validation": "true",
    "final_optimization": "false"
}

NSGA2_CHS_PARAMS = {
    "mvmo_algorithm": "classic_ga",
    "feature_importance_categorical": "lasso",
    "sorting_strategy": "crowding_distance_clone_index",
    "use_clone_repurposing": "true",
    "bitlist_mutation_operator": "symm",
    "external_dataset": "swedish",
    "cross_validation": "true",
    "final_optimization": "false"
}

ALGORITHMS_DICT = {
    "moabc": MOABC_LASSO,
    "moabc_no_lasso": MOABC_UNIFORM,
    "nsga2": NSGA2_PARAMS,
    "nsga2_ch": NSGA2_CH_PARAMS,
    "nsga2_chs": NSGA2_CHS_PARAMS
}

# =====================================================================
# 2. GESTIÓN DE RUTAS Y MÉTRICAS
# =====================================================================

def get_expected_monomer_path(dataset, model, algo_name, args):
    obj_map = {"naive_bayes": "NB_bal_acc_leanness", "RF": "RF_bal_acc_leanness", "svm": "leanness_svm_bal_acc"}
    obj_dir = obj_map.get(model, "unknown_obj")
    outer_folds = "2" if args.setup == "small" else "5"
    inner = "2" if args.setup == "small" else "3"
    pop, gen = str(args.pop), str(args.gen)
    
    if algo_name in ["moabc", "moabc_no_lasso"]:
        p = ALGORITHMS_DICT[algo_name]
        dE, dO = int(float(p["moabc_p_watering_emp"]) * 100), int(float(p["moabc_p_prune_obs"]) * 100)
        base = f"moabc_p{pop}_ev{args.evals}_dE{dE}_dO{dO}_L{p['limit']}"
        fi = p.get("feature_importance_categorical", "none")
        suffix = "_(MV_lassoFI,none)" if fi == "lasso" else "_(none,none)"
        opt_dir = f"{base}_{args.nick}{suffix}" if args.nick else f"{base}{suffix}"
    elif algo_name == "nsga2":
        opt_dir = f"NSGA2_k{inner}_pop{pop}_uni0-50_gen{gen}_CrowdFull_c0.33_m1.0flip_(none,none)"
    elif algo_name == "nsga2_ch":
        opt_dir = f"NSGA2_k{inner}_pop{pop}_uni0-50_gen{gen}_CrowdCI_c0.33_m1.0flip_(MV_lassoFI,none)"
    elif algo_name == "nsga2_chs":
        opt_dir = f"NSGA2_k{inner}_pop{pop}_uni0-50_gen{gen}_CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)"
    else: opt_dir = "unknown_algo"

    return os.path.join(os.getcwd(), dataset, "mrna", obj_dir, f"{outer_folds}_folds", opt_dir)

def extract_metrics_from_csvs(target_dir):
    hof_dir = os.path.join(target_dir, "hofs", "Pareto")
    if not os.path.exists(hof_dir): return None, None, None
    fit_files = sorted(glob.glob(os.path.join(hof_dir, "solution_fitnesses_fold_*.csv")))
    feat_files = sorted(glob.glob(os.path.join(hof_dir, "solution_features_fold_*.csv")))
    if not fit_files or not feat_files: return None, None, None
    
    try:
        cross_hv_list, fold_jaccards = [], []
        for fit_f, feat_f in zip(fit_files, feat_files):
            df_fit = pd.read_csv(fit_f)
            df_feat = pd.read_csv(feat_f)
            
            feature_names = df_feat.columns.tolist()
            gene_lists = [[name for name, val in zip(feature_names, row) if val == 1] for _, row in df_feat.iterrows()]
            fold_jaccards.append(compute_jaccard_from_lists(gene_lists))
            
            train_col = next((c for c in df_fit.columns if "inner_cv" in c or "train_" in c), None)
            test_col = next((c for c in df_fit.columns if "test_" in c), None)
            lean_col = next((c for c in df_fit.columns if "leanness" in c), None)
            if train_col and test_col and lean_col:
                tr_boxes = [ConcreteHyperbox0B.create_by_b_vals((r[train_col], r[lean_col])) for _, r in df_fit.iterrows()]
                te_boxes = [ConcreteHyperbox0B.create_by_b_vals((r[test_col], r[lean_col])) for _, r in df_fit.iterrows()]
                cross_hv_list.append(cross_hypervolume(tr_boxes, te_boxes))
        return np.mean(cross_hv_list), np.std(cross_hv_list), np.mean(fold_jaccards)
    except Exception:
        return None, None, None

# =====================================================================
# 3. GENERACIÓN DINÁMICA DE CONFIGURACIONES (.INI)
# =====================================================================

def generate_ini(dataset, model, algo_name, exp_id, args, mission_name):
    config = configparser.ConfigParser(); config.optionxform = str  
    setup_dict = ALGORITHMS_DICT[algo_name].copy()
    
    setup_dict.update({
        "dataset": dataset, 
        "pop": str(args.pop),
        "objectives": f'[["bal_acc", "{model}"], "leanness"]',
        "initial_features_strategy": "uniform",
        "initial_features_min": "0",
        "initial_features_max": "50"
    })
    
    if args.setup == "big": 
        setup_dict.update({"use_big_defaults": "true", "inner_n_folds": "3"})
    else: 
        setup_dict.update({"use_big_defaults": "false", "inner_n_folds": "2"})
        
    if algo_name in ["moabc", "moabc_no_lasso"]: 
        setup_dict.update({"moabc_max_evals": str(args.evals), "moabc_exp_version": args.nick})
    else: 
        setup_dict["generations"] = f"[{args.gen}]"
        if "bitlist_mutation_operator" not in setup_dict:
            setup_dict["bitlist_mutation_operator"] = "flip"
    
    os.makedirs(os.path.join("setups", mission_name), exist_ok=True)
    ini_path = os.path.join("setups", mission_name, f"{exp_id}.ini")
    with open(ini_path, 'w') as f: 
        config["MVMOO_SETUP"] = setup_dict
        config.write(f)
        
    return ini_path

def execute_task(task_info):
    dataset, model, algo_name, exp_id, args, mission_name, n_cpus = task_info
    ini_path = generate_ini(dataset, model, algo_name, exp_id, args, mission_name)
    
    env = os.environ.copy(); env["MONOMER_CPUS"] = str(n_cpus)
    log_dir = os.path.join("tuning_reports", mission_name, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{exp_id}.log")

    print(f"    [STARTED] {exp_id}...")
    with open(log_file, "w") as f:
        subprocess.run(["python", "../py/run_with_setups.py", ini_path], 
                       env=env, stdout=f, stderr=subprocess.STDOUT)
    print(f"    [FINISHED] {exp_id}")
    return exp_id

# =====================================================================
# 4. ORQUESTADOR SECUENCIAL EN DOS FASES
# =====================================================================

def main():
    global_start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fast', 'complete'], default='complete')
    parser.add_argument('--setup', choices=['small', 'big'], default='small')
    parser.add_argument('--pop', type=int)
    parser.add_argument('--gen', type=int)
    parser.add_argument('--evals', type=int)
    parser.add_argument('--nick', default="")
    args = parser.parse_args()

    # Defaults setup (Mapeado del Mini-Experimento)
    if args.setup == 'small':
        args.pop = args.pop or 48      # Por defecto 48 (divisible por 4) para evitar selTournament crash
        args.gen = args.gen or 100     
        args.evals = args.evals or 5000 
    elif None in [args.pop, args.gen, args.evals]:
        print("[!] Error: setup 'big' requiere pop, gen y evals."); sys.exit(1)

    # RESTRICCIÓN DE MOTOR DEAP: La población DEBE ser divisible por 4
    if args.pop % 4 != 0:
        original_pop = args.pop
        args.pop = ((args.pop + 2) // 4) * 4
        print(f"[*] AJUSTE DE RECURSOS: Redondeando población de {original_pop} a {args.pop} para cumplir con selTournament de DEAP (múltiplo de 4).")

    current_datasets = ALL_DATASETS.copy()
    if args.setup == 'small':
        current_datasets = [f"{ds}_mini" for ds in ALL_DATASETS]

    MISSION_NAME = f"Mision_{args.mode}_{args.setup}_{args.nick}"
    report_dir = os.path.join("tuning_reports", MISSION_NAME); os.makedirs(report_dir, exist_ok=True)
    
    nsga_queue = []
    moabc_queue = []

    for ds in current_datasets:
        for mod in ALL_MODELS:
            # Baselines (Fase 1)
            for alg in ["nsga2", "nsga2_ch", "nsga2_chs"]:
                eid = f"{alg}_{args.setup}_{args.nick}_{ds}_{mod}"
                nsga_queue.append((ds, mod, alg, eid))
            # MOABCs (Fase 2)
            for alg in ["moabc", "moabc_no_lasso"]:
                eid = f"{alg}_{args.setup}_{args.nick}_{ds}_{mod}"
                moabc_queue.append((ds, mod, alg, eid))

    cpus_per_task = 8
    max_workers = 4

    # =====================================================================
    # FASE 1: EJECUCIÓN DE BASELINES (NSGA-II) + SMART SKIPPING
    # =====================================================================
    phase_1_start = time.time()
    print(f"\n{'='*85}\n FASE 1: PROCESAMIENTO DE BASELINES ESTÁTICOS (NSGA-II)\n{'='*85}")
    
    pending_nsga = []
    for ds, mod, alg, eid in nsga_queue:
        target_dir = get_expected_monomer_path(ds, mod, alg, args)
        if os.path.exists(target_dir) and extract_metrics_from_csvs(target_dir)[0] is not None:
            pass
        else:
            pending_nsga.append((ds, mod, alg, eid, args, MISSION_NAME, cpus_per_task))

    if pending_nsga:
        print(f"[*] SMART SKIPPING: {len(nsga_queue) - len(pending_nsga)} baselines ya resueltos en disco.")
        print(f"[*] Lanzando {len(pending_nsga)} ejecuciones NSGA-II pendientes ({max_workers} en paralelo)...\n")
        with ProcessPoolExecutor(max_workers=max_workers) as exe:
            list(exe.map(execute_task, pending_nsga))
    else:
        print("[+] SMART SKIPPING: El 100% de los baselines NSGA-II ya existen en disco. Omitiendo Fase 1.")
        
    p1_time = int(time.time() - phase_1_start)
    print(f"\n[+] Fase 1 concluida en: {p1_time // 60}m {p1_time % 60}s")

    # =====================================================================
    # FASE 2: ENJAMBRE MOABC (CON Y SIN LASSO)
    # =====================================================================
    phase_2_start = time.time()
    print(f"\n{'='*85}\n FASE 2: PROCESAMIENTO DE ENJAMBRES MOABC V2 (CON Y SIN LASSO)\n{'='*85}")
    
    pending_moabc = []
    for ds, mod, alg, eid in moabc_queue:
        target_dir = get_expected_monomer_path(ds, mod, alg, args)
        if os.path.exists(target_dir) and extract_metrics_from_csvs(target_dir)[0] is not None:
            pass
        else:
            pending_moabc.append((ds, mod, alg, eid, args, MISSION_NAME, cpus_per_task))

    if pending_moabc:
        print(f"[*] SMART SKIPPING: {len(moabc_queue) - len(pending_moabc)} enjambres MOABC ya resueltos.")
        print(f"[*] Lanzando {len(pending_moabc)} ejecuciones MOABC pendientes ({max_workers} en paralelo)...\n")
        with ProcessPoolExecutor(max_workers=max_workers) as exe:
            list(exe.map(execute_task, pending_moabc))
    else:
        print("[+] SMART SKIPPING: El 100% de los enjambres MOABC ya existen en disco. Omitiendo Fase 2.")
        
    p2_time = int(time.time() - phase_2_start)
    print(f"\n[+] Fase 2 concluida en: {p2_time // 60}m {p2_time % 60}s")

    # =====================================================================
    # 5. RECOMPILACIÓN DE RESULTADOS Y GUARDADO DE REPORTE CSV
    # =====================================================================
    print(f"\n{'='*85}\n COMPILANDO REPORTE FINAL MULTI-FIDELITY\n{'='*85}")
    results_summary = []
    
    for ds, mod, alg, eid in (nsga_queue + moabc_queue):
        target_dir = get_expected_monomer_path(ds, mod, alg, args)
        mean_hv, std_hv, mean_jac = extract_metrics_from_csvs(target_dir)
        
        if mean_hv is not None:
            fi = ALGORITHMS_DICT[alg].get("feature_importance_categorical", "none")
            results_summary.append({
                "Dataset": ds,
                "Model": mod,
                "Experimento": eid,
                "FI_Mode": fi,
                "Mean_LCB": round(mean_hv - std_hv, 4),
                "Mean_Jac": round(mean_jac, 4)
            })

    if results_summary:
        df_res = pd.DataFrame(results_summary)
        print(df_res.to_string(index=False))
        csv_file = os.path.join(report_dir, f"{MISSION_NAME}_report.csv")
        df_res.to_csv(csv_file, index=False)
        print(f"\n[+] Reporte completo guardado con éxito en: {csv_file}")
    else:
        print("[!] No se pudieron extraer datos de rendimiento para el reporte.")

    total_seg = int(time.time() - global_start_time)
    d, resto = divmod(total_seg, 86400); h, resto = divmod(resto, 3600); m, s = divmod(resto, 60)
    print(f"\n{'='*85}\n TIEMPO TOTAL DE LA SUITE COMPLETA: {d:02d}-{h:02d}:{m:02d}:{s:02d}\n{'='*85}\n")

if __name__ == "__main__":
    main()