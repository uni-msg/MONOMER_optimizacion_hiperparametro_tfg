from hyperparameter_evolution.svm_hyperparameter_set_factory import SVMHyperparameterSetFactory
from hyperparameter_evolution.forest_hyperparameter_set_factory import ForestHyperparameterSetFactory
from hyperparameter_evolution.logistic_hyperparameter_set_factory import LogisticHyperparameterSetFactory
from hyperparameter_evolution.nb_hyperparameter_set_factory import NBHyperparameterSetFactory
from hyperparameter_evolution.hyperparameter_set_factory import HyperparameterSetFactory
from model.model import  DEFAULT_LOGISTIC_MAX_ITER
from model.svm import SVMWithFallback
from setup.allowed_names import NAIVE_BAYES_NAME, LOGISTIC_NAME, FOREST_NAME

def parse_hyperparameter_set_factory(model_str: str, logistic_max_iter: int = DEFAULT_LOGISTIC_MAX_ITER, use_hyperparameter_evolution: bool = False) -> HyperparameterSetFactory | None:
    """
    Devuelve la fábrica de conjuntos de hiperparámetros correspondiente al
    modelo de clasificación configurado en el setup.
    """
    if not use_hyperparameter_evolution:
        return None

    if model_str == NAIVE_BAYES_NAME:
        return NBHyperparameterSetFactory()
    elif model_str == LOGISTIC_NAME:
        return LogisticHyperparameterSetFactory(max_iter=logistic_max_iter)
    elif model_str == FOREST_NAME:
        return ForestHyperparameterSetFactory()
    elif model_str == SVMWithFallback().nick():
        return SVMHyperparameterSetFactory()
    else:
        raise ValueError( f"Unknown model for hyperparameter evolution: {model_str}" )
