from collections.abc import Sequence
from random import choice
from typing import Optional

from hyperparameter_evolution.hyperparameter import Hyperparameter


class CategoricalHyperparameter(Hyperparameter):
    __option_values: tuple[str, ...]

    def __init__(
        self,
        nick: str,
        name: str,
        option_values: Sequence[str],
        value: Optional[str] = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

        self.__option_values = tuple(option_values)

        if len(self.__option_values) == 0:
            raise ValueError("option_values no puede estar vacío")

        if value is not None and value not in self.__option_values:
            raise ValueError("El valor inicial no pertenece a los valores permitidos")

    def option_values(self) -> tuple[str]:
        return self.__option_values

    def random_initialize(self):
        """
        Asigna aleatoriamente uno de los valores permitidos.
        """
        if not self.mutable():
            return
        
        self.set_value(choice(self.__option_values)) #Se transforma en tupla para poder usar choice

    def mutate(self):
        """
        Muta el hiperparámetro a otro valor distinto del actual.
        """
        if not self.mutable():
            return
        
        current = self.value()

        # Si todavía no tiene valor, lo inicializamos
        if current is None:
            self.random_initialize()
            return

        # Si solo existe una opción, no hay nada que mutar
        if len(self.option_values()) == 1:
            return

        #Recoge las opciones que no sean el valor actual
        options = tuple(
            value
            for value in self.option_values()
            if value != current
        )

        self.set_value(choice(options))

    def crossover(self, other):
        """
        Realiza un crossover uniforme con otro hiperparámetro categórico.
        """
        #Bloque seguridad
        if not isinstance(other, CategoricalHyperparameter):
            raise TypeError("El crossover requiere otro CategoricalHyperparameter")
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