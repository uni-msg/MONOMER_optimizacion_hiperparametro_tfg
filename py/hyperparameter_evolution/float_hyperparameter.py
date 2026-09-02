from random import uniform
from typing import Optional
from deap import tools

from hyperparameter_evolution.hyperparameter import Hyperparameter


class FloatHyperparameter(Hyperparameter):
    __lower_bound: float
    __upper_bound: float

    def __init__(
        self,
        nick: str,
        name: str,
        lower_bound: float,
        upper_bound: float,
        value: Optional[float] = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

        if lower_bound > upper_bound:
            raise ValueError("lower_bound debe ser mas pequeño a upper_bound")

        self.__lower_bound = lower_bound
        self.__upper_bound = upper_bound

    def lower_bound(self) -> float:
        return self.__lower_bound

    def upper_bound(self) -> float:
        return self.__upper_bound

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
        Aplica Polynomial Mutation respetando los límites del hiperparámetro.
        """
        if not self.mutable():
            return

        current = self.value()

        # Si no tiene valor, lo inicializamos aleatoriamente
        if current is None:
            self.random_initialize()
            return

        mutated, = tools.mutPolynomialBounded(
            [current],
            eta=100.0, # Valor recomendado para Polynomial Mutation según Deb & Deb (2014)
            low=self.lower_bound(),
            up=self.upper_bound(),
            indpb=1.0 #Probabilidad gestionada por el conjunto
        )

        print(f"FLOAT: {current} -> {mutated[0]}")
        self.set_value(mutated[0])

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