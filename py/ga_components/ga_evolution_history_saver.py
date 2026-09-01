from abc import ABC, abstractmethod
from consts import GA_EVOLUTION_HISTORY_PREFIX
from ga_components.ga_evolution_history import GAEvolutionHistory
import json
import os



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
    def save(self, evolution_histories: dict[str, GAEvolutionHistory]):
        """
        Funcion abstracta que posibilita las diferentes formas de almacenar el archivo (Json, YAML, Csv..)
        """
        raise NotImplementedError()


class DummyGAEvolutionHistorySaver(GAEvolutionHistorySaver):

    def save(self, evolution_histories: dict[str, GAEvolutionHistory]):
        pass


class JsonGAEvolutionHistorySaver(GAEvolutionHistorySaver):
    """
    Clase encargada del almacenar un objeto GAEvolutionHistory dentro de una ruta especifica con un archivo Json 
    """
    __directory: str
    __final_str: str

    def __init__(self, directory: str, final_str: str):
        self.__directory = directory
        self.__final_str = final_str

    def save(self, evolution_histories: dict[str, GAEvolutionHistory]):
        for hof_nick, evolution_history in evolution_histories.items():
            hof_dir = os.path.join(self.__directory, hof_nick)
            os.makedirs(hof_dir, exist_ok=True)
            file = os.path.join(hof_dir,GA_EVOLUTION_HISTORY_PREFIX + self.__final_str + ".json")
            ga_evolution_history_to_json(evolution_history=evolution_history,file=file)

