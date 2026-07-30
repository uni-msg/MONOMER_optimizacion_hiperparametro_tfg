from hyperparameter_evolution.categorical_hyperparameter import (
    CategoricalHyperparameter,
)
from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from hyperparameter_evolution.hyperparameter_set_factory import HyperparameterSetFactory
from hyperparameter_evolution.integer_hyperparameter import IntegerHyperparameter
from hyperparameter_evolution.log_float_hyperparameter import LogFloatHyperparameter
from model.model import DEFAULT_LOGISTIC_MAX_ITER


class LogisticHyperparameterSetFactory(HyperparameterSetFactory):

    __max_iter: int

    def __init__(self, max_iter: int = DEFAULT_LOGISTIC_MAX_ITER):
        self.__max_iter = max_iter

    def create(self) -> HyperparameterSet:
        return HyperparameterSet(
            nick="LOGIT_HPE",
            name="Logistic Regression Hyperparameters",
            hyperparameters=[

                # Inversa de la fuerza de regularización.
                # Valores pequeños implican una regularización más fuerte,
                # mientras que valores grandes permiten modelos más complejos.
                LogFloatHyperparameter(
                    nick="C",
                    name="Inverse regularization strength",
                    lower_bound=1e-4,
                    upper_bound=100.0,
                    mutation_factor=0.3
                ),

                # Tolerancia empleada como criterio de parada del optimizador.
                # Valores menores requieren una convergencia más precisa,
                # aumentando el tiempo de entrenamiento.
                LogFloatHyperparameter(
                    nick="tol",
                    name="Stopping tolerance",
                    lower_bound=1e-6,
                    upper_bound=1e-2,
                    mutation_factor=0.2
                ),

                #################### FIJOS ####################

                # Número máximo de iteraciones permitidas durante el proceso
                # de optimización. Si el algoritmo no converge antes,
                # finalizará al alcanzar este límite. Se define en el setup
                IntegerHyperparameter(
                    nick="max_iter",
                    name="Maximum iterations",
                    lower_bound=self.__max_iter,
                    upper_bound=self.__max_iter,
                    mutation_range=self.__max_iter,
                    value=self.__max_iter,
                    mutable=False
                ),

                # Algoritmo de optimización utilizado durante el entrenamiento.
                # MONOMER emplea actualmente LBFGS por su estabilidad y buen
                # rendimiento en la mayoría de problemas.
                CategoricalHyperparameter(
                    nick="solver",
                    name="Solver",
                    options={"lbfgs"},
                    value="lbfgs",
                    mutable=False
                ),

                # Tipo de regularización aplicada.
                # Actualmente se mantiene sin penalización para seguir el
                # comportamiento implementado originalmente en MONOMER.
                # A partir de scikit-learn 1.10 este parámetro desaparecerá y
                # será sustituido por la combinación de C y l1_ratio.
                CategoricalHyperparameter(
                    nick="penalty",
                    name="Penalty",
                    options={"none"},
                    value="none",
                    mutable=False
                ),

                # Número de hilos utilizados durante el entrenamiento.
                # Se mantiene fijo para evitar diferencias debidas al
                # paralelismo y mantener la reproducibilidad.
                # A partir de scikit-learn 1.10 este parámetro desaparecerá
                IntegerHyperparameter(
                    nick="n_jobs",
                    name="Number of jobs",
                    lower_bound=1,
                    upper_bound=1,
                    mutation_range=1,
                    value=1,
                    mutable=False
                ),

                # TODO:
                # Implementar l1_ratio cuando se soporte la evolución
                # de hiperparámetros con dependencias entre ellos
                # (penalty, solver y l1_ratio).
            ]
        )