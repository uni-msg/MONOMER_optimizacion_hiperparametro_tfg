import os
import random
import numpy as np

def probe_rng_and_population(algorithm_nick, fold, population, active_features=None):
    """
    Guarda el estado del RNG y la población para depuración forense.
    """
    base_dir = "temp/rng_forensics"
    os.makedirs(base_dir, exist_ok=True)
    
    # --- 1. CAPTURA DEL ESTADO DEL RNG ---
    # getstate() devuelve (version, internal_state_tuple, gauss_next)
    # internal_state_tuple tiene 624 enteros de 32 bits.
    rng_state = random.getstate()
    internal_array = rng_state[1]
    
    # Creamos una firma simple sumando los valores internos. 
    # Si cambia un solo número aleatorio consumido antes, esta suma cambiará.
    rng_signature = sum(internal_array)
    
    # --- 2. CAPTURA DE FEATURES ACTIVAS ---
    active_sum = -1
    if active_features is not None:
        active_sum = np.sum(active_features)

    # --- 3. GUARDADO EN FICHERO ---
    filename = os.path.join(base_dir, f"{algorithm_nick}_fold{fold}_forensics.txt")
    
    with open(filename, "w") as f:
        f.write(f"=== RNG FORENSICS FOR {algorithm_nick} (Fold {fold}) ===\n")
        f.write(f"RNG SIGNATURE (The 'N' value): {rng_signature}\n")
        f.write(f"RNG Full State (First 10 values): {internal_array[:10]}...\n")
        f.write(f"Active Features Sum: {active_sum}\n")
        f.write(f"Total Individuals: {len(population)}\n")
        f.write("-" * 30 + "\n")
        f.write("GENES DUMP (First 10 individuals):\n")
        
        # Guardamos los primeros 10 para no llenar el disco, o todos si prefieres
        for i, ind in enumerate(population[:20]):
            # Convertimos a string binario
            genes = "".join(str(int(x)) for x in ind)
            f.write(f"Ind_{i}: {genes}\n")

    print(f"--- [PROBE] Forensics dumped to {filename} (Sig: {rng_signature}) ---")