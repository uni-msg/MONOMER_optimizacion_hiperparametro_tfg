import numpy as np
import time
import random
from deap import tools

# =====================================================================
# CONFIGURACIÓN DE CARGA PESADA (HPC STRESS TEST)
# =====================================================================
N_POP = 5000       # Tamaño de población para tests individuales
N_ARC = 20000      # Tamaño de archivo para particionamiento
N_POOL = 10000     # Tamaño de pool para filtrado Pareto (Cuidado: O(N^2) en Python)
N_ITER = 100       # Repeticiones para suavizar promedios
NICHE_BOUNDARIES = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 100)
TOLERANCE = 0.005

# Generación de datos sintéticos
pop_acc = np.random.uniform(0.6, 0.95, N_POP)
pop_size = np.random.randint(1, 150, N_POP)
child_acc = pop_acc + np.random.uniform(-0.01, 0.01, N_POP)
child_size = pop_size + np.random.randint(-2, 3, N_POP)
arc_size = np.random.randint(1, 150, N_ARC)

print(f"{'='*60}")
print(f" BENCHMARK: PYTHON (MOABC ACTUAL) vs NUMPY (PROPUESTA)")
print(f" Configuración: Pop={N_POP}, Arc={N_ARC}, Pool Pareto={N_POOL}")
print(f"{'='*60}\n")

# =====================================================================
# TEST 1: ASIGNACIÓN DE NICHOS
# =====================================================================
print("TEST 1: ASIGNACIÓN DE NICHOS (Bucketing)")

def niches_python(sizes, boundaries):
    results = []
    for s in sizes:
        bucket = len(boundaries)
        for i, b in enumerate(boundaries):
            if s <= b:
                bucket = i
                break
        results.append(bucket)
    return results

def niches_numpy(sizes, boundaries):
    return np.digitize(sizes, boundaries, right=True)

t0 = time.time()
for _ in range(N_ITER):
    res_py = niches_python(pop_size, NICHE_BOUNDARIES)
t_py = (time.time() - t0) / N_ITER

t0 = time.time()
for _ in range(N_ITER):
    res_np = niches_numpy(pop_size, NICHE_BOUNDARIES)
t_np = (time.time() - t0) / N_ITER

print(f"  > Python (promedio): {t_py:.8f}s")
print(f"  > Numpy  (promedio): {t_np:.8f}s")
print(f"  > MEJORA: {t_py/t_np:.2f}x")
print(f"  > IDENTIDAD: {np.array_equal(res_py, res_np)}\n")


# =====================================================================
# TEST 2: REGLA DE REEMPLAZO ELÁSTICO
# =====================================================================
print("TEST 2: REGLA DE REEMPLAZO ELÁSTICO (Lógica de Decisión)")

def replacement_python(p_acc, p_size, c_acc, c_size, tol):
    keep_child = []
    for i in range(len(p_acc)):
        c_dom = (c_acc[i] >= p_acc[i] and c_size[i] <= p_size[i]) and (c_acc[i] > p_acc[i] or c_size[i] < p_size[i])
        if c_dom:
            keep_child.append(True)
        elif (p_acc[i] >= c_acc[i] and p_size[i] <= c_size[i]):
            keep_child.append(False)
        else:
            delta_acc, delta_size = c_acc[i] - p_acc[i], c_size[i] - p_size[i]
            keep_child.append(delta_acc > (delta_size * tol))
    return keep_child

def replacement_numpy(p_acc, p_size, c_acc, c_size, tol):
    delta_acc, delta_size = c_acc - p_acc, c_size - p_size
    c_dom = ((c_acc >= p_acc) & (c_size <= p_size)) & ((c_acc > p_acc) | (c_size < p_size))
    p_dom = ((p_acc >= c_acc) & (p_size <= c_size)) & ((p_acc > c_acc) | (p_size < c_size))
    elastic = delta_acc > (delta_size * tol)
    return c_dom | (~p_dom & (delta_size != 0) & elastic)

t0 = time.time()
for _ in range(N_ITER):
    res_py = replacement_python(pop_acc, pop_size, child_acc, child_size, TOLERANCE)
t_py = (time.time() - t0) / N_ITER

t0 = time.time()
for _ in range(N_ITER):
    res_np = replacement_numpy(pop_acc, pop_size, child_acc, child_size, TOLERANCE)
t_np = (time.time() - t0) / N_ITER

print(f"  > Python (promedio): {t_py:.8f}s")
print(f"  > Numpy  (promedio): {t_np:.8f}s")
print(f"  > MEJORA: {t_py/t_np:.2f}x")
print(f"  > IDENTIDAD: {np.array_equal(res_py, res_np)}\n")


# =====================================================================
# TEST 3: PARTICIONADO DE ARCHIVO PARA LÍDER
# =====================================================================
print("TEST 3: PARTICIONADO DE ARCHIVO (Líder Bimodal)")

def pick_bimodal_python(archive_sizes, boundaries, bee_bucket):
    local_indices, far_indices = [], []
    for idx, size in enumerate(archive_sizes):
        a_bucket = len(boundaries)
        for i, b in enumerate(boundaries):
            if size <= b:
                a_bucket = i
                break
        if abs(a_bucket - bee_bucket) <= 1: local_indices.append(idx)
        else: far_indices.append(idx)
    return local_indices, far_indices

def pick_bimodal_numpy(archive_sizes, boundaries, bee_bucket):
    a_buckets = np.digitize(archive_sizes, boundaries, right=True)
    is_local = np.abs(a_buckets - bee_bucket) <= 1
    return np.where(is_local)[0], np.where(~is_local)[0]

bee_bucket_test = 4
t0 = time.time()
for _ in range(N_ITER):
    l_py, f_py = pick_bimodal_python(arc_size, NICHE_BOUNDARIES, bee_bucket_test)
t_py = (time.time() - t0) / N_ITER

t0 = time.time()
for _ in range(N_ITER):
    l_np, f_np = pick_bimodal_numpy(arc_size, NICHE_BOUNDARIES, bee_bucket_test)
t_np = (time.time() - t0) / N_ITER

print(f"  > Python (promedio): {t_py:.8f}s")
print(f"  > Numpy  (promedio): {t_np:.8f}s")
print(f"  > MEJORA: {t_py/t_np:.2f}x")
print(f"  > IDENTIDAD LOCAL: {set(l_py) == set(l_np)}")
print(f"  > IDENTIDAD FAR:   {set(f_py) == set(f_np)}\n")


# =====================================================================
# TEST 4: FILTRADO PARETO RANK 1
# =====================================================================
print(f"TEST 4: FILTRADO PARETO RANK 1 (Pool de {N_POOL} individuos)")
print("  (Aviso: Esto puede tardar unos segundos...)")

class MockFitness:
    def __init__(self, values):
        self.values = values
        self.valid = True
    def dominates(self, other):
        return all(x >= y for x, y in zip(self.values, other.values)) and \
               any(x > y for x, y in zip(self.values, other.values))

class MockInd:
    def __init__(self, fit_vals):
        self.fitness = MockFitness(fit_vals)

pool_fits = np.random.uniform(0.7, 0.95, (N_POOL, 2))
pool_fits[:, 1] = -np.random.randint(1, 200, N_POOL)
pool_inds = [MockInd(tuple(f)) for f in pool_fits]

def pareto_rank1_DEAP(inds):
    return tools.sortNondominated(inds, len(inds), first_front_only=True)[0]

def pareto_rank1_NUMPY(inds):
    fits = np.array([ind.fitness.values for ind in inds])
    n = fits.shape[0]
    is_efficient = np.ones(n, dtype=bool)
    for i in range(n):
        if is_efficient[i]:
            # Vectorización: comprobamos contra todos los que quedan
            # El individuo i domina a j si fits[i] >= fits[j]
            dominated = np.all(fits[i] >= fits, axis=1) & np.any(fits[i] > fits, axis=1)
            is_efficient[dominated] = False
    return [inds[i] for i in np.where(is_efficient)[0]]

t0 = time.time()
res_deap = pareto_rank1_DEAP(pool_inds)
t_deap = time.time() - t0

t0 = time.time()
res_np = pareto_rank1_NUMPY(pool_inds)
t_np = time.time() - t0

print(f"  > DEAP sortNondominated: {t_deap:.4f}s")
print(f"  > Numpy Vectorized:      {t_np:.4f}s")
print(f"  > MEJORA: {t_deap/t_np:.2f}x")
print(f"  > MISMO RESULTADO: {len(res_deap) == len(res_np)}")

print(f"\n{'='*60}")
print(" FIN DEL BENCHMARK")
print(f"{'='*60}")