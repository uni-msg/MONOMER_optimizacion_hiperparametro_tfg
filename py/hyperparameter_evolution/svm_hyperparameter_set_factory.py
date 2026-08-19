from hyperparameter_evolution.boolean_hyperparameter import BooleanHyperparameter
from hyperparameter_evolution.categorical_hyperparameter import (
    CategoricalHyperparameter,
)
from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from hyperparameter_evolution.hyperparameter_set_factory import HyperparameterSetFactory
from hyperparameter_evolution.log_float_hyperparameter import LogFloatHyperparameter


class SVMHyperparameterSetFactory(HyperparameterSetFactory):

    def create(self) -> HyperparameterSet:
        return HyperparameterSet(
            nick="SVM_HPE",
            name="Support Vector Machine Hyperparameters",
            hyperparameters=[

                # Controla la fuerza de regularización del clasificador.
                # Valores pequeños permiten un margen más amplio y un modelo
                # más simple. Valores grandes penalizan más los errores de
                # clasificación y generan fronteras de decisión más complejas.
                LogFloatHyperparameter(
                    nick="C",
                    name="Regularization parameter",
                    lower_bound=1e-3,
                    upper_bound=100.0,
                    mutation_range=0.3
                ),

                # Determina el radio de influencia de cada muestra cuando se
                # utiliza el kernel RBF.
                # Valores pequeños generan fronteras más suaves.
                # Valores grandes permiten fronteras mucho más complejas,
                # aumentando el riesgo de overfitting.
                LogFloatHyperparameter(
                    nick="gamma",
                    name="Kernel coefficient",
                    lower_bound=1e-6,
                    upper_bound=1.0,
                    mutation_range=0.2
                ),

                # Tolerancia utilizada por el criterio de parada del algoritmo
                # de optimización. Valores menores hacen que el entrenamiento
                # continúe hasta encontrar una solución más precisa, aunque
                # requieren más tiempo de ejecución.
                LogFloatHyperparameter(
                    nick="tol",
                    name="Stopping tolerance",
                    lower_bound=1e-5,
                    upper_bound=1e-2,
                    mutation_range=0.2
                ),

                #################### FIJOS ####################

                # Indica si durante el entrenamiento se utiliza la heurística
                # de shrinking para acelerar la resolución del problema de
                # optimización. 
                # MONOMER lo mantiene activado ya que únicamente influye en el
                # proceso de optimización y no modifica el problema que se resuelve.
                BooleanHyperparameter(
                    nick="shrinking",
                    name="Use shrinking heuristic",
                    value=True,
                    mutable=False
                ),

                # Función kernel empleada por el SVM para transformar los datos
                # a un espacio donde puedan separarse de forma no lineal.
                # MONOMER utiliza actualmente únicamente el kernel RBF.
                CategoricalHyperparameter(
                    nick="kernel",
                    name="Kernel",
                    option_values={"rbf"},
                    value="rbf",
                    mutable=False
                ),

                # Estrategia utilizada para compensar conjuntos de datos
                # desbalanceados. El valor "balanced" ajusta automáticamente
                # el peso de cada clase según su frecuencia en el conjunto
                # de entrenamiento.
                CategoricalHyperparameter(
                    nick="class_weight",
                    name="Class weight",
                    option_values={"balanced"},
                    value="balanced",
                    mutable=False
                ),

                # TODO:
                # Implementar la evolución del kernel. Su incorporación requiere
                # soportar hiperparámetros dependientes, ya que cada kernel utiliza
                # un conjunto distinto de hiperparámetros (gamma, degree, coef0, etc.).
            ]
        )

    def nick(self) -> str:
        return "SVMHyperparameterSetFactory"

    def name(self) -> str:
        return "Fabrica de conjunto Support Vector Machine Hyperparameters"