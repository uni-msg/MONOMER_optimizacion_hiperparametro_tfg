import json
from copy import deepcopy
from typing import Sequence

from individual.peculiar_individual import PeculiarIndividual


class GAEvolutionHistory:
    """
    Almacena la evolución de la población del algoritmo genético.

    Se guarda un registro por generación y, dentro de cada generación,
    la información de todos los individuos de la población.

    La información almacenada de cada individuo incluye:
        - hiperparámetros
        - fitness
        - características activas
    """

    def __init__(self):
        self.__generations = []

    def add_generation(self, generation: int, population: Sequence[PeculiarIndividual]):
        """
        Añade una generación al historial.

        Se almacena una copia independiente de la información de los
        individuos para evitar que posteriores modificaciones de la
        población alteren el historial.
        """
        individuals = []

        for individual in population:
            individual_data = {
                "id": getattr(individual, "history_index", None),
                "hyperparameters": self.__get_hyperparameters(individual),
                "fitness": self.__get_fitness(individual),
                "features": self.__get_features(individual)
            }

            individuals.append(individual_data)

        self.__generations.append({
            "generation": generation,
            "individuals": individuals
        })
    @staticmethod
    def __get_hyperparameters(individual):
        """
        Obtiene el conjunto de hiperparámetros del individuo.
        """
        if individual.has_hyperparameter_set():
            return deepcopy(individual.hyperparameter_set().to_dict())

        return None

    @staticmethod
    def __get_fitness(individual):
        """
        Obtiene el fitness del individuo.
        """
        if individual.has_fitness():
            return deepcopy(individual.fitness.as_list())

        return None

    @staticmethod
    def __get_features(individual):
        """
        Obtiene las posiciones de las características activas del individuo.
        """
        return list(individual.true_positions())

    def generations(self):
        """
        Devuelve las generaciones almacenadas.
        """
        return self.__generations

    def to_dict(self):
        """
        Convierte el historial completo a un diccionario.
        """
        return {
            "generations": deepcopy(self.__generations)
        }

    def save(self, file: str):
        """
        Guarda el historial completo en formato JSON.
        """
        with open(file, "w", encoding="utf-8") as f:
            json.dump(
                self.to_dict(),
                f,
                indent=4,
                ensure_ascii=False
            )