from math import log10
from random import uniform
from deap import tools

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

    def crossover(self, other):
        """
        Realiza un Simulated Binary Crossover (SBX) sobre la escala
        logarítmica de dos hiperparámetros.
        """
        #Bloque seguridad
        if not isinstance(other, LogFloatHyperparameter):
            raise TypeError("El crossover requiere otro LogFloatHyperparameter")
        if not self.mutable() or not other.mutable():
            return self, other
        if self.value() is None or other.value() is None:
            return self, other

        # Cruce SBX logaritmica, similar al mutate
        child1, child2 = tools.cxSimulatedBinaryBounded(
            [log10(self.value())],
            [log10(other.value())],
            eta=20.0,
            low=log10(self.lower_bound()),
            up=log10(self.upper_bound())
        )

        # Volvemos de escala logarítmica a escala normal
        self.set_value(10 ** child1[0])
        other.set_value(10 ** child2[0])

        return self, other