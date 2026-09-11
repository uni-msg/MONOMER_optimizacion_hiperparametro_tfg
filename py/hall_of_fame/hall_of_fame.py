from abc import abstractmethod
from collections import Iterable

from hall_of_fame.hofers import Hofers
from hall_of_fame.population_observer import PopulationObserver
from util.named import NickNamed


class HallOfFame(PopulationObserver, NickNamed):

    @abstractmethod
    def add(self, elem):
        """The new element is deepcopied."""
        raise NotImplementedError()

    def update(self, new_elems: Iterable):
        """The new elements are deepcopied."""
        for e in new_elems:
            self.add(e)

    @abstractmethod
    def hofers(self) -> Hofers:
        """The returned Hofers are a deepcopy of the internal data."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self) -> Iterable:
        """
        Devuelve la colección interna del Hall of Fame sin realizar una copia.

        Este método es únicamente de lectura inmediata. No se debe modificar
        la colección ni conservar la referencia devuelta.
        """
        raise NotImplementedError()
