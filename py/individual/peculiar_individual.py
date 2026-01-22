from abc import abstractmethod
from typing import Sequence
import numpy as np  # Necesario para active_features_mask y sum

from individual.fitness.peculiar_fitness import PeculiarFitness
from individual.predictive_individual import PredictiveIndividual


class PeculiarIndividual(PredictiveIndividual):
    fitness: PeculiarFitness

    def __init__(self, n_objectives: int):
        PredictiveIndividual.__init__(self, fitness=PeculiarFitness(n_objectives=n_objectives))
        # Inicializamos explícitamente la lista de predictores
        self.__predictors = []

    @abstractmethod
    def get_stat(self, name):
        raise NotImplementedError()

    @abstractmethod
    def get_stats(self):
        """Object returned is a copy."""
        raise NotImplementedError()

    @abstractmethod
    def get_crowding_distance(self):
        return self.fitness.get_crowding_distance()

    @abstractmethod
    def get_peculiarity(self):
        return self.fitness.get_peculiarity()

    @abstractmethod
    def get_social_space(self):
        return self.fitness.get_social_space()

    # --- IMPLEMENTACIÓN DE PREDICTORES (CRÍTICO PARA HOF SAVER) ---
    def get_predictors(self):
        """Devuelve la lista de predictores asociados al individuo."""
        return self.__predictors

    def set_predictors(self, predictors):
        """Asigna la lista de predictores."""
        self.__predictors = predictors

    # --- MÉTODOS PARA MÉTRICAS DE DIVERSIDAD (Jaccard) ---
    def active_features_mask(self):
        """Devuelve el propio individuo como máscara para jaccard_score."""
        return self

    def sum(self):
        """Suma de características activas."""
        return sum(self)

    def true_positions(self):
        """Índices activos (fallback para individuos densos)."""
        return [i for i, x in enumerate(self) if x]