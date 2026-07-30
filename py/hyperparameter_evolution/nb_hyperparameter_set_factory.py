from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from hyperparameter_evolution.hyperparameter_set_factory import HyperparameterSetFactory
from hyperparameter_evolution.log_float_hyperparameter import LogFloatHyperparameter


class NBHyperparameterSetFactory(HyperparameterSetFactory):

    def create(self) -> HyperparameterSet:
        return HyperparameterSet(
            nick="NB_HPE",
            name="Naive Bayes Hyperparameters",
            hyperparameters=[

                # Cantidad de suavizado que se añade a la varianza para evitar
                # problemas numéricos cuando una característica tiene varianza
                # extremadamente pequeña o nula.
                LogFloatHyperparameter(
                    nick="var_smoothing",
                    name="Variance smoothing",
                    lower_bound=1e-12,
                    upper_bound=1e-6,
                    mutation_factor=0.2
                )

            ]
        )