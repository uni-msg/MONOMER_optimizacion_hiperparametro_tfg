from abc import ABC, abstractmethod
from ga_components.ga_evolution_history import GAEvolutionHistory
import json


def ga_evolution_history_to_json(evolution_history: GAEvolutionHistory,file: str):
    """
    Funcion que transforma los datos recibidos de un objeto GAEvolutionHistory a Json
    """

    with open(file, "w", encoding="utf-8") as fileW:
        json.dump(evolution_history.to_dict(), fileW, indent=4,ensure_ascii=False)


class GAEvolutionHistorySaver(ABC):
    """
    Clase base encargada de definir un  metodo de guardado permanente de datos de un objeto GaEvolutionHistory
    Sigue implementaciones similares a logbook_saver.py
    """

    @abstractmethod
    def save(self, evolution_history: GAEvolutionHistory):
        """
        Funcion abstracta que posibilita las diferentes formas de almacenar el archivo (Json, YAML, Csv..)
        """
        raise NotImplementedError()


class DummyGAEvolutionHistorySaver(GAEvolutionHistorySaver):

    def save(self, evolution_history: GAEvolutionHistory):
        pass


class JsonGAEvolutionHistorySaver(GAEvolutionHistorySaver):
    """
    Clase encargada del almacenar un objeto GAEvolutionHistory dentro de una ruta especifica con un archivo Json 
    """
    __file: str

    def __init__(self, file: str):
        self.__file = file

    def save(self, evolution_history: GAEvolutionHistory):
        ga_evolution_history_to_json(
            evolution_history=evolution_history,
            file=self.__file)
