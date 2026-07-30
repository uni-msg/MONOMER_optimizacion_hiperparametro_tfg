from collections.abc import Sequence
from random import choice

from hyperparameter_evolution.hyperparameter import Hyperparameter


class CategoricalHyperparameter(Hyperparameter):
    __option_values: set[str]

    def __init__(
        self,
        nick: str,
        name: str,
        option_values: Sequence[str],
        value: str | None = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

        self.__option_values = set(option_values)

        if len(self.__option_values) == 0:
            raise ValueError("option_values no puede estar vacío")

        if value is not None and value not in self.__option_values:
            raise ValueError("El valor inicial no pertenece a los valores permitidos")

    def option_values(self) -> set[str]:
        return self.__option_values

    def random_initialize(self):
        """
        Asigna aleatoriamente uno de los valores permitidos.
        """
        if not self.mutable():
            return
        
        self.set_value(choice(tuple(self.option_values()))) #Se transforma en tupla para poder usar choice

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