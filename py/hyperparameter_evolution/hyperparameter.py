from abc import ABC, abstractmethod
from copy import deepcopy


class Hyperparameter(ABC):
    """
    Clase base para almacenar la informacion de los hiperparametros
    Se emplean subtipos: boolean/float/integer/categorical 
    """
    __nick : str
    __name : str
    __value : object
    __mutable : bool

    def __init__(self, nick: str, name: str, value = None, mutable: bool = True):
        self.__nick = nick
        self.__name = name
        self.__value = value
        self.__mutable = mutable

    def nick(self) -> str:
        return self.__nick

    def name(self) -> str:
        return self.__name

    def value(self) :
        return self.__value

    def set_value(self, value):
        self.__value = value

    def mutable(self) -> bool:
        return self.__mutable

    def to_dict(self):
        return {
            "name": self.name(),
            "nick": self.nick(),
            "value": self.value(),
            "mutable": self.mutable()
        }

    @abstractmethod
    def random_initialize(self):
        """
        Inicializa el hiperparametro de manera aleatoria 
        """
        raise NotImplementedError()

    @abstractmethod
    def mutate(self):
        """
        Muta de manera aleatoria el valor del hiperparametro
        """
        raise NotImplementedError()

    @abstractmethod
    def crossover(self, other):
        """
        Cruza un hiperparametro con otro del mismo tipo
        """
        raise NotImplementedError()

    def __str__(self):
        return f"{self.nick()} = {self.value()}"
    
    def __eq__(self, hyperparameter) -> bool:    
        if not isinstance(hyperparameter, Hyperparameter):
            return False
 
        if self is hyperparameter:
            return True
        
        return self.nick() == hyperparameter.nick() and self.value() == hyperparameter.value() 

    def __ne__(self, hyperparameter) -> bool:
        return not self == hyperparameter