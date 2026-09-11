import json
from copy import deepcopy
from typing import Optional
from individual.peculiar_individual_with_context import PeculiarIndividualWithContext
from deap.tools import History


class GAEvolutionHistory:
    """
    Almacena la evolución de los resultados del HOF del algoritmo genético.

    Para cada generación se guarda la información de los individuos del HOF.

    La información de cada individuo incluye:
        - generación
        - hiperparámetros
        - fitness
        - características activas
    """

    def __init__(self, file: Optional[str] = None):
        self.__file = file
        self.__generations = [] if file is None else None

    def add_generation(self, generation: int, population , history: Optional[History] = None):
        """
        Añade una generación al historial.

        Se almacena una copia de la información de los individuos 
        para evitar que posteriores modificaciones de la
        población alteren el historial.
        """
        individuals = []
        for individual in population:
            individual_data = {
                #"id": getattr(individual, "history_index", None),
                #"parents": self.__get_parents(individual_id=individual_id,history=history),
                "hyperparameters": self.__get_hyperparameters(individual),
                "fitness": self.__get_fitness(individual),
                "features": self.__get_features(individual)
            }

            #Se añade a la lista
            individuals.append(individual_data)

        #Añadis lista de individuos seleccionados por generacion
        generation_data={
            "generation": generation,
            "individuals": individuals
        }

        # Si tenemos fichero, escribimos esta generación inmediatamente.
        if self.__file is not None:
            try:
                with open(self.__file, "a", encoding="utf-8") as file_w:
                    json.dump(
                        generation_data,
                        file_w,
                        ensure_ascii=False
                    )
                    file_w.write("\n")
                    file_w.flush() 

            except Exception as e:
                print(
                    f"WARNING: Could not save GA evolution history "
                    f"to '{self.__file}': {e}"
                )

        # Si no tenemos fichero, mantenemos el comportamiento antiguo.
        else:
            self.__generations.append(generation_data)

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

