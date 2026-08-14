from random import uniform
from typing import Optional
from deap import tools

from hyperparameter_evolution.hyperparameter import Hyperparameter


class FloatHyperparameter(Hyperparameter):
    __lower_bound: float
    __upper_bound: float
    __mutation_range: float

    def __init__(
        self,
        nick: str,
        name: str,
        lower_bound: float,
        upper_bound: float,
        mutation_range: Optional[float] = None,
        value: Optional[float] = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

        if lower_bound > upper_bound:
            raise ValueError("lower_bound debe ser mas pequeño a upper_bound")

        if mutation_range is not None and mutation_range <= 0:
            raise ValueError("mutation_range debe ser mayor a 0")

        self.__lower_bound = lower_bound
        self.__upper_bound = upper_bound
        self.__mutation_range = mutation_range

    def lower_bound(self) -> float:
        return self.__lower_bound

    def upper_bound(self) -> float:
        return self.__upper_bound

    def mutation_range(self) -> float:
        return self.__mutation_range

    def random_initialize(self):
        """
        Asigna un valor float al azar, sin salir de las cotas
        """
        if not self.mutable():
            return
        
        self.set_value(
            uniform(self.lower_bound(), self.upper_bound())
        )

    def mutate(self):
        """
        Muta el valor del hiperparámetro según el rango de mutación
        """
        if not self.mutable():
            return
        
        current = self.value()

        # Si todavía no tiene valor o no tiene rango de mutación, lo inicializamos
        if current is None or self.mutation_range() is None:
            self.random_initialize()
            return

        displacement = uniform(-self.mutation_range(),self.mutation_range())

        new_value = current + displacement

        # Respetar límites
        new_value = max(self.lower_bound(), new_value)
        new_value = min(self.upper_bound(), new_value)

        self.set_value(new_value)

    def crossover(self, other):
        """
        Realiza un Simulated Binary Crossover (SBX) con otro
        hiperparámetro float del mismo tipo.
        """
        #Bloque seguridad
        if not isinstance(other, FloatHyperparameter):
            raise TypeError("El crossover requiere otro FloatHyperparameter")
        if not self.mutable() or not other.mutable():
            return self, other
        if self.value() is None or other.value() is None:
            return self, other

        #Cruce SBX
        child1, child2 = tools.cxSimulatedBinaryBounded([self.value()],[other.value()],eta=20.0,low=self.lower_bound(),up=self.upper_bound())

        self.set_value(child1[0])
        other.set_value(child2[0])

        return self, other