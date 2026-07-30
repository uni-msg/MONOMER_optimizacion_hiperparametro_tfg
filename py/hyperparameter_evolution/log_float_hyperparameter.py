from math import log10
from random import uniform

from hyperparameter_evolution.float_hyperparameter import FloatHyperparameter


class LogFloatHyperparameter(FloatHyperparameter):
    """
    Hiperparámetro de tipo float cuya inicialización y mutación se realizan
    en escala logarítmica. (bastante empleadas en algunos hiperparametros)
    """

    def random_initialize(self):
        """
        Asigna un valor aleatorio utilizando una distribución uniforme
        en escala log10.
        """
        if not self.mutable():
            return

        exponent = uniform(
            log10(self.lower_bound()),
            log10(self.upper_bound())
        )

        self.set_value(10 ** exponent)

    def mutate(self):
        """
        Muta el hiperparámetro desplazando su exponente en escala logarítmica.
        """
        if not self.mutable():
            return

        current = self.value()

        if current is None:
            self.random_initialize()
            return

        exponent = log10(current)

        exponent += uniform(
            -self.mutation_range(),
            self.mutation_range()
        )

        lower = log10(self.lower_bound())
        upper = log10(self.upper_bound())

        exponent = max(lower, min(upper, exponent))

        self.set_value(10 ** exponent)