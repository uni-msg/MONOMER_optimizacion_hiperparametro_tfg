from abc import ABC, abstractmethod

from hyperparameter_evolution.hyperparameter_set import HyperparameterSet


class HyperparameterSetFactory(ABC):
    """
    Factoría encargada de construir un HyperparameterSet
    para un algoritmo de clasificación concreto.
    """

    @abstractmethod
    def create(self) -> HyperparameterSet:
        """
        Crea un conjunto de hiperparámetros con la estructura
        correspondiente al algoritmo de clasificacion específico.
        """
        raise NotImplementedError()

    @abstractmethod
    def nick(self) -> str:
        """
        Nick correspondente a la factoría
        """
        raise NotImplementedError()

    @abstractmethod
    def name(self) -> str:
        """
        Name correspondente a la factoría
        """
        raise NotImplementedError()

    def __str__(self):
        return self.nick()