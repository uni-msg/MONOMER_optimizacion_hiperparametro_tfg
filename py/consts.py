from model.model_with_coef import NBWithFallback

DEFAULT_RECURSION_LIMIT = 100000  # At least 20000 needed when pickling big objects.
DEFAULT_MODEL = NBWithFallback()
GEN_STR = "gen"
FOLD_RES_DATA_PREFIX = "log_fold_"
FOLD_RES_DATA_EXTENSION = "csv"
GENERATION_FEATURES_STRING = "gen_feats"
EXPLORED_FEATURES_STRING = "explored"
FEATURE_COUNTS_PREFIX = "feature_counts_"
FEATURE_COUNTS_EXTENSION = "csv"

#Contador de hiperparametros
HYPERPARAMETER_COUNTS_PATH = "hyperparameters/"

#Historial de la evolcion de los individuos
GA_EVOLUTION_HISTORY_PREFIX = "ga_evolution_history_"
GA_EVOLUTION_HISTORY_EXTENSION = "jsonl"
DIR_HOFS = "hofs"

FINAL_STR = "final"
DEFAULT_FOLD_PARALLELISM = True
MAX_WORKERS = 256
FONT_SIZE = 11
