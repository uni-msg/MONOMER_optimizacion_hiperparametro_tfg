from random import randint
from typing import Optional
from deap import tools

from hyperparameter_evolution.hyperparameter import Hyperparameter


class IntegerHyperparameter(Hyperparameter):
    __lower_bound: int
    __upper_bound: int

    def __init__(
        self,
        nick: str,
        name: str,
        lower_bound: int,
        upper_bound: int,
        value: Optional[int] = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

        if lower_bound > upper_bound:
            raise ValueError("lower_bound debe ser mas pequeño a upper_bound")

        self.__lower_bound = lower_bound
        self.__upper_bound = upper_bound

    def lower_bound(self) -> int:
        return self.__lower_bound

    def upper_bound(self) -> int:
        return self.__upper_bound

    def random_initialize(self):
        """
        Asigna un valor integer al azar, sin salir de las cotas
        """
        if not self.mutable():
            return
        
        self.set_value(
            randint(self.lower_bound(), self.upper_bound())
        )

    def mutate(self):
        """
        Aplica Polynomial Mutation respetando los límites del hiperparámetro.
        El resultado se redondea para mantener el valor entero.
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
            eta=20.0,
            low=self.lower_bound(),
            up=self.upper_bound(),
            indpb=1.0
        )

        # Convertir a entero y respetar los límites
        new_value = int(round(mutated[0]))

        # En el caso que el redondeo haya ocultado valor se va a un vecino proximo
        if new_value == current:
            if mutated[0] > current:
                new_value = current + 1
            elif mutated[0] < current:
                new_value = current - 1

        new_value = max(self.lower_bound(), new_value)
        new_value = min(self.upper_bound(), new_value)
        
        self.set_value(new_value)

    def crossover(self, other):
        """
        Realiza un Simulated Binary Crossover (SBX) con otro
        hiperparámetro entero del mismo tipo.
        """
        #Bloque seguridad
        if not isinstance(other, IntegerHyperparameter):
            raise TypeError("El crossover requiere otro IntegerHyperparameter")
        if not self.mutable() or not other.mutable():
            return self, other
        if self.value() is None or other.value() is None:
            return self, other

        #Crossover SBX
        child1, child2 = tools.cxSimulatedBinaryBounded([self.value()],[other.value()],eta=20.0,low=self.lower_bound(),up=self.upper_bound())

        # Asegurar que siguen dentro de los límites y SBX sea valor entero
        child1_value = max(self.lower_bound(),min(self.upper_bound(), int(round(child1[0]))))
        child2_value = max(other.lower_bound(),min(other.upper_bound(), int(round(child2[0]))))

        self.set_value(child1_value)
        other.set_value(child2_value)

        return self, other