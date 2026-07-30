from hyperparameter_evolution.categorical_hyperparameter import (
    CategoricalHyperparameter,
)
from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from hyperparameter_evolution.hyperparameter_set_factory import HyperparameterSetFactory
from hyperparameter_evolution.integer_hyperparameter import IntegerHyperparameter


class ForestHyperparameterSetFactory(HyperparameterSetFactory):

    def create(self) -> HyperparameterSet:
        return HyperparameterSet(
            nick="RF_HPE",
            name="Random Forest Hyperparameters",
            hyperparameters=[

                # Número de árboles que forman el bosque.
                # Un mayor número suele mejorar la estabilidad del modelo,
                # aunque incrementa el tiempo de entrenamiento.
                IntegerHyperparameter(
                    nick="n_estimators",
                    name="Number of trees",
                    lower_bound=10,
                    upper_bound=300,
                    mutation_range=20
                ),

                # Número mínimo de muestras necesarias para dividir un nodo.
                # Valores mayores producen árboles menos profundos y reducen
                # el riesgo de overfitting.
                IntegerHyperparameter(
                    nick="min_samples_split",
                    name="Minimum samples split",
                    lower_bound=2,
                    upper_bound=20,
                    mutation_range=2
                ),

                # Número mínimo de muestras que debe contener una hoja.
                # Incrementar este valor suaviza el modelo y mejora su capacidad
                # de generalización.
                IntegerHyperparameter(
                    nick="min_samples_leaf",
                    name="Minimum samples leaf",
                    lower_bound=1,
                    upper_bound=20,
                    mutation_range=2
                ),

                # Número máximo de características consideradas al buscar la mejor
                # división de cada nodo.
                # - "sqrt": utiliza la raíz cuadrada del número total de características.
                # - "log2": utiliza el logaritmo en base 2 del número de características.
                # - None: utiliza todas las características disponibles.
                # Hay otras opciones pero no aportan lo suficiente
                CategoricalHyperparameter(
                    nick="max_features",
                    name="Maximum features",
                    options={"sqrt", "log2", None}
                ),

                #################### FIJOS ####################

                # Estrategia utilizada para compensar conjuntos de datos
                # desbalanceados.
                CategoricalHyperparameter(
                    nick="class_weight",
                    name="Class weight",
                    options={"balanced"},
                    value="balanced",
                    mutable=False
                ),

                # Número de procesos utilizados durante el entrenamiento.
                IntegerHyperparameter(
                    nick="n_jobs",
                    name="Number of jobs",
                    lower_bound=1,
                    upper_bound=1,
                    mutation_range=1,
                    value=1,
                    mutable=False
                )
            ]
        )