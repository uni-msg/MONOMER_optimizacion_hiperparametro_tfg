import json
from copy import deepcopy
from typing import Optional
from individual.peculiar_individual_with_context import PeculiarIndividualWithContext
from deap.tools import History


class GAEvolutionHistory:
    """
    Almacena la evolución de la población seleccionada del algoritmo genético.

    Para cada generación se guarda la información de todos los individuos
    que sobreviven a la selección.

    La información de cada individuo incluye:
        - ID genealógico asignado por DEAP
        - IDs de sus padres
        - generación
        - hiperparámetros
        - fitness
        - características activas
    """

    def __init__(self):
        self.__generations = []

    def add_generation(self, generation: int, population , history: Optional[History] = None):
        """
        Añade una generación al historial.

        Se almacena una copia de la información de los individuos 
        para evitar que posteriores modificaciones de la
        población alteren el historial.

        Se aprovecha el History de DEAP para la genealogía del individuo
        """
        individuals = []
        for i, individual in enumerate(population):
            #Identificador del History
            individual_id = getattr(individual, "history_index", None)

            individual_data = {
                #"id": individual_id,
                #"parents": self.__get_parents(individual_id=individual_id,history=history),
                "hyperparameters": self.__get_hyperparameters(individual),
                "fitness": self.__get_fitness(individual),
                "features": self.__get_features(individual)
            }

            #Se añade a la lista
            individuals.append(individual_data)

        #Añadis lista de individuos seleccionados por generacion
        self.__generations.append({
            "generation": generation,
            "individuals": individuals
        })

    @staticmethod
    def __get_parents(individual_id: Optional[int], history: Optional[History]) -> list[int]:
        """
        Obtiene los IDs de los padres directos de un individuo
        usando la genealogía de DEAP.
        """

        if history is None or individual_id is None:
            return []

        #Recupera los padres del individuo buscado
        parents = history.genealogy_tree.get(individual_id)

        if parents is None:
            return []

        return list(parents) #1 ID = mutacion, 2 IDs = crossover

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