from copy import deepcopy
import random

from hyperparameter_evolution.hyperparameter import Hyperparameter


class HyperparameterSet:
    """
    Clase que se encarga de almacenar un diccionario de hyperparametros
    """
    __nick : str
    __name : str
    __hyperparameters: dict[str, Hyperparameter]

    def __init__(self, nick: str, name: str, hyperparameters=None):
        self.__nick = nick
        self.__name = name
        self.__hyperparameters = {}

        #Recorremos la lista de hiperparametros
        if hyperparameters is not None:
            for hyperparameter in hyperparameters:
                self.add(hyperparameter)

    def nick(self) -> str:
        return self.__nick

    def name(self) -> str:
        return self.__name
    

    def add(self, hyperparameter: Hyperparameter):
        """
        Añade un hiperparámetro al conjunto.
        El nick debe ser único y se aprovecha el del hyperparametro.
        """
        self.__hyperparameters[hyperparameter.nick()] = hyperparameter

    def get(self, nick: str) -> Hyperparameter:
        return self.__hyperparameters[nick]

    def remove(self, nick: str):
        del self.__hyperparameters[nick]

    def contains(self, nick: str) -> bool:
        return nick in self.__hyperparameters

    def values(self):
        return self.__hyperparameters.values()

    def items(self):
        return self.__hyperparameters.items()
    

    def random_initialize(self):
        """
        Inicializa aleatoriamente todos los hiperparámetros.
        """
        for hyperparameter in self.values():
            hyperparameter.random_initialize()

    def mutate(self, mutation_probability: float):
        """
        Muta cada hiperparámetro de forma independiente según
        la probabilidad de mutación indicada.
        """
        for hyperparameter in self.values():
            if hyperparameter.mutable() and random.random() < mutation_probability:
                old_value = hyperparameter.value()

                hyperparameter.mutate()

                print(
                    f"\n[HPE MUTATION] {hyperparameter.nick()}"
                    f"\n  Antes:  {old_value}"
                    f"\n  Después: {hyperparameter.value()}"
                )

    def crossover(self, other):
        """
        Realiza el crossover entre dos conjuntos de hiperparámetros.

        Cada hiperparámetro se cruza con su correspondiente hiperparámetro
        del otro conjunto si tenen el mismo nick.
        """
        #Proteccion de errores
        if not isinstance(other, HyperparameterSet):
            raise TypeError( "El crossover requiere otro HyperparameterSet")
        if self.nick() != other.nick():
            raise ValueError("No se pueden cruzar HyperparameterSet de distinto tipo")
        if set(self.__hyperparameters.keys()) != set(other.__hyperparameters.keys()):
            raise ValueError("Los HyperparameterSet no contienen los mismos hiperparámetros")

        #Bucle de crossover de mismos hp
        for nick, hyperparameter in self.items():
            other_hyperparameter = other.get(nick)
            if type(hyperparameter) is not type(other_hyperparameter):
                raise TypeError(f"Los hiperparámetros '{nick}' deben ser del mismo tipo")
            print(
                f"\n[HPE CROSSOVER] {nick}"
                f"\n  Padre 1: {hyperparameter.value()}"
                f"\n  Padre 2: {other_hyperparameter.value()}"
            )

            hyperparameter.crossover(other_hyperparameter)

            print(
                f"  Hijo 1:  {hyperparameter.value()}"
                f"\n  Hijo 2:  {other_hyperparameter.value()}"
            )



        return self, other

    def clone(self):
        return deepcopy(self)
    
    def hyperparameters_to_kwargs(self):
        """
        Formatea los datos de nick y valor para emplearse en la definicion del modelo de manera general
        """
        return {
            hyperparameter.nick(): hyperparameter.value()
            for hyperparameter in self.values()
        }

    def to_dict(self):
        return {
            "name": self.name(),
            "nick": self.nick(),
            "hyperparameters": {
                nick: hyperparameter.to_dict()
                for nick, hyperparameter in self.items()
            }
        }

    def __len__(self):
        return len(self.__hyperparameters)

    def __iter__(self):
        return iter(self.values())

    def __getitem__(self, nick: str) -> Hyperparameter:
        return self.get(nick)

    def __str__(self):
        return "\n".join(
            str(hyperparameter)
            for hyperparameter in self.values()
        )

    def __eq__(self, other):
        if not isinstance(other, HyperparameterSet):
            return False
        return ( self.nick() == other.nick() and self.__hyperparameters == other.__hyperparameters )

    def __ne__(self, other):
        return not self == other