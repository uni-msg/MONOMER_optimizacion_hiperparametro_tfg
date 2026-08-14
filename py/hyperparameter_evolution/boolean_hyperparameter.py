from random import choice
from typing import Optional

from hyperparameter_evolution.hyperparameter import Hyperparameter


class BooleanHyperparameter(Hyperparameter):

    def __init__(
        self,
        nick: str,
        name: str,
        value: Optional[bool] = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

    def random_initialize(self):
        """
        Asigna un valor booleano al azar.
        """
        if not self.mutable():
            return
        
        self.set_value(
            choice([True, False])
        )

    def mutate(self):
        """
        Invierte el valor del hiperparámetro.
        """
        if not self.mutable():
            return
        
        current = self.value()

        # Si todavía no tiene valor, lo inicializamos
        if current is None:
            self.random_initialize()
            return

        self.set_value(not current)

    def crossover(self, other):
        """
        Realiza un crossover uniforme con otro hiperparámetro booleano.
        """
        #Bloque seguridad
        if not isinstance(other, BooleanHyperparameter):
            raise TypeError("El crossover requiere otro BooleanHyperparameter")
        if not self.mutable() or not other.mutable():
            return self, other
        if self.value() is None or other.value() is None:
            return self, other

        #Cruce uniforme
        if choice([True, False]): #Probabilidad del 50% de que se intercambien los valores
            self_value = self.value()
            other_value = other.value()

            self.set_value(other_value)
            other.set_value(self_value)

        return self, other