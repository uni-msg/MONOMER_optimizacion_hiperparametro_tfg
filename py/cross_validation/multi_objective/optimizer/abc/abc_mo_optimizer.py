from collections import Iterable, Sequence
import random
import numpy as np

from deap import tools

from cross_validation.multi_objective.optimizer.ga_str_utils import nick_paste, pop_nick, gen_nick, \
    sorting_strategy_nick_part, mutation_nick_part, name_paste, pop_name, gen_name, \
    sorting_strategy_name_part, mutation_name_part
from cross_validation.multi_objective.optimizer.mo_optimizer_type import MOOptimizerType
from cross_validation.multi_objective.optimizer.multi_objective_optimizer import MultiObjectiveOptimizerResult, \
    hofs_to_results, hofers_to_results
from cross_validation.multi_objective.optimizer.multi_objective_optimizer_accepting_feature_importance import \
    MultiObjectiveOptimizerAcceptingFeatureImportance
from folds_creator.input_data_folds_creator import InputDataFoldsCreator
from ga_components.bitlist_mutation import BitlistMutation, FlipMutation
from ga_components.feature_counts_saver import FeatureCountsSaver, DummyFeatureCountsSaver
from ga_components.logbook_saver import LogbookSaver, DummyLogbookSaver
from ga_components.sorter.sorting_strategy import SortingStrategy
from hall_of_fame.population_observer_factory import HallOfFameFactory, ParetoFrontFactory
from individual.num_features import NumFeatures
from input_data.input_data import InputData
from input_data.input_data_utils import select_outcomes_in_objectives
from univariate_feature_selection.univariate_feature_selection import compute_active_features_sv_multi_target
from objective.social_objective import PersonalObjective
from util.distribution.distribution import Distribution
from util.printer.printer import Printer, UnbufferedOutPrinter
from util.randoms import random_seed, set_all_seeds
from util.utils import name_value
from ga_strategy.ga_strategy_bitlist import GAStrategyBitlist
from evaluator.workers_pool_evaluator import WorkersPoolEvaluator
from hyperparam_manager.dummy_hp_manager import DummyHpManager


class ABCType(MOOptimizerType):
    def name(self) -> str: return "Artificial Bee Colony"
    def nick(self) -> str: return "abc_mo"
    def uses_inner_models(self) -> bool: return True


class AbcMoOptimizer(MultiObjectiveOptimizerAcceptingFeatureImportance):
    __objectives: Iterable[PersonalObjective]
    __sorting_strategy: SortingStrategy
    __hof_factories: Iterable[HallOfFameFactory]
    __nick: str
    __name: str
    __folds_creator: InputDataFoldsCreator
    __mutation: BitlistMutation
    __initial_features: NumFeatures
    __optimizer_type: MOOptimizerType

    def __init__(self, pop_size, n_gen, limit,
                 initial_features: NumFeatures,
                 folds_creator: InputDataFoldsCreator,
                 objectives: Iterable[PersonalObjective],
                 sorting_strategy: SortingStrategy,
                 hof_factories: Iterable[HallOfFameFactory] = (ParetoFrontFactory(),),
                 mutation: BitlistMutation = FlipMutation(),
                 use_clone_repurposing: bool = False,
                 mutation_frequency: float = 0.05):
        
        self.__pop_size = pop_size 
        self.__n_gen = n_gen       
        self.__limit = limit       
        self.__use_clone_repurposing = use_clone_repurposing
        self.__mutation_frequency = mutation_frequency
        
        self.__initial_features = initial_features
        self.__folds_creator = folds_creator
        self.__objectives = objectives
        self.__sorting_strategy = sorting_strategy
        self.__hof_factories = hof_factories
        self.__mutation = mutation
        self.__optimizer_type = ABCType()

        self.__nick = nick_paste(parts=[self.__optimizer_type.nick(),
                                        self.__folds_creator.nick(),
                                        pop_nick(pop_size=pop_size),
                                        initial_features.nick(),
                                        gen_nick(n_gen=n_gen),
                                        sorting_strategy_nick_part(sorting_strategy=sorting_strategy, 
                                                                   use_clone_repurposing=use_clone_repurposing),
                                        mutation_nick_part(mutation=mutation, 
                                                           mutation_frequency=mutation_frequency),
                                        f"lim{limit}"
                                        ])
        
        self.__name = self.__optimizer_type.name() + " (" + name_paste(parts=[
            self.__folds_creator.name(),
            pop_name(pop_size=pop_size),
            initial_features.name(),
            gen_name(n_gen=n_gen),
            sorting_strategy_name_part(sorting_strategy=sorting_strategy, 
                                       use_clone_repurposing=use_clone_repurposing),
            mutation_name_part(mutation=mutation, 
                               mutation_frequency=mutation_frequency),
            f"Limit: {limit}"
        ]) + ")"

    def optimize_with_feature_importance(
            self, input_data: InputData, printer: Printer,
            feature_importance: Sequence[Distribution],
            n_proc=1, workers_printer: Printer = UnbufferedOutPrinter(),
            logbook_saver: LogbookSaver = DummyLogbookSaver(),
            feature_counts_saver: FeatureCountsSaver = DummyFeatureCountsSaver()) -> [MultiObjectiveOptimizerResult]:
        
        set_all_seeds(772346)

        input_data = select_outcomes_in_objectives(input_data=input_data, objectives=self.__objectives)
        collapsed_views = input_data.collapsed_views()
        
        printer.title_print("Computing local active features (ABC)")
        active_features = compute_active_features_sv_multi_target(
            collapsed_views, input_data.collapsed_outcomes(), printer=printer, n_proc=n_proc)
        
        # --- FIX: FORZAR NUMPY ARRAY (para mutación simétrica en _chs) ---
        active_features = np.array(active_features)
        
        printer.title_print("Creating inner folds")
        folds_list = self.__folds_creator.create_folds_from_input_data(input_data=input_data, seed=random_seed())

        printer.title_print("Running Artificial Bee Colony Optimization")

        ga_strategy = GAStrategyBitlist(
            input_data=input_data,
            folds_list=folds_list,
            objectives=self.__objectives,
            sorting_strategy=self.__sorting_strategy,
            initial_features=self.__initial_features,
            mutation=self.__mutation,
            mating_prob=0.0, 
            mutation_frequency=self.__mutation_frequency, 
            active_features=active_features,
            feature_importance=feature_importance,
            n_workers=n_proc,
            workers_printer=workers_printer,
            use_clone_repurposing=self.__use_clone_repurposing
        )

        stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "limit_hits", "avg", "min", "max"

        hofs = [h.create_population_observer() for h in self.__hof_factories]

        hp_manager = DummyHpManager()
        
        evaluator = WorkersPoolEvaluator(
            input_data=input_data,
            folds_list=folds_list,
            hp_manager=hp_manager,
            objectives=self.__objectives,
            n_workers=n_proc,
            workers_printer=workers_printer
        )

        final_results = None

        try:
            # --- Inicialización ---
            population = [ga_strategy.create_individual() for _ in range(self.__pop_size)]
            
            pre_creation_state = random.getstate()
            pre_creation_signature = sum(pre_creation_state[1])
            
            population = [ga_strategy.create_individual() for _ in range(self.__pop_size)]
            
            # Ahora guardamos el informe usando la firma que capturamos ANTES
            probe_rng_and_population(
                algorithm_nick=self.nick(),
                fold="X", # O usa una variable si la tienes
                population=population,
                active_features=active_features
            )
            # Hack para imprimir la firma en el log estándar también
            printer.print(f"DEBUG: RNG Signature BEFORE population creation: {pre_creation_signature}")
            # ---------------------------

            # evaluate(keep_predictors=False) por defecto
            self._evaluate_population(evaluator, population, keep_predictors=False)

            # evaluate(keep_predictors=False) por defecto
            self._evaluate_population(evaluator, population, keep_predictors=False)
            
            trials = [0] * self.__pop_size
            for h in hofs: h.update(population)

            record = stats.compile(population)
            logbook.record(gen=0, evals=len(population), limit_hits=0, **record)
            printer.print(logbook.stream)
            
            # Feature Counts Gen 0
            feature_names = collapsed_views.columns
            counts = [0] * len(feature_names)
            for ind in population:
                if hasattr(ind, 'true_positions'): 
                    for pos in ind.true_positions():
                        counts[pos] += 1
                else:
                    for idx, val in enumerate(ind):
                        if val: counts[idx] += 1
            feature_counts_saver.save(feature_counts=[counts], feature_names=feature_names)

            # --- Bucle Evolutivo ---
            for cycle in range(1, self.__n_gen + 1):
                
                # 1. Abejas Empleadas
                offspring_employed = []
                for i in range(self.__pop_size):
                    neighbor = self.__mutation.mutate(
                        individual=population[i], 
                        frequency=self.__mutation_frequency,
                        active_mask=active_features
                    )
                    neighbor = neighbor[0] if isinstance(neighbor, tuple) else neighbor
                    offspring_employed.append(neighbor)
                
                self._evaluate_population(evaluator, offspring_employed, keep_predictors=False)

                for i in range(self.__pop_size):
                    if offspring_employed[i].fitness.dominates(population[i].fitness):
                        population[i] = offspring_employed[i]
                        trials[i] = 0
                    else:
                        trials[i] += 1

                # 2. Abejas Observadoras
                population = list(self.__sorting_strategy.apply_before_selection(
                    pop=population, 
                    hp_manager=hp_manager
                ))
                
                offspring_onlooker = []
                target_indices = []
                
                for _ in range(self.__pop_size):
                    ind1 = random.randint(0, self.__pop_size - 1)
                    ind2 = random.randint(0, self.__pop_size - 1)
                    parent_idx = ind1 if ind1 < ind2 else ind2
                    target_indices.append(parent_idx)
                    
                    neighbor = self.__mutation.mutate(
                        individual=population[parent_idx], 
                        frequency=self.__mutation_frequency,
                        active_mask=active_features
                    )
                    neighbor = neighbor[0] if isinstance(neighbor, tuple) else neighbor
                    offspring_onlooker.append(neighbor)
                
                self._evaluate_population(evaluator, offspring_onlooker, keep_predictors=False)

                for i in range(self.__pop_size):
                    target_idx = target_indices[i]
                    if offspring_onlooker[i].fitness.dominates(population[target_idx].fitness):
                        population[target_idx] = offspring_onlooker[i]
                        trials[target_idx] = 0
                    else:
                        trials[target_idx] += 1

                # 3. Abejas Exploradoras
                n_scouts = 0
                new_scouts = []
                scout_indices = []
                
                for i in range(self.__pop_size):
                    if trials[i] > self.__limit:
                        new_ind = ga_strategy.create_individual()
                        new_scouts.append(new_ind)
                        scout_indices.append(i)
                        trials[i] = 0
                        n_scouts += 1
                
                if n_scouts > 0:
                    self._evaluate_population(evaluator, new_scouts, keep_predictors=False)
                    for k, idx in enumerate(scout_indices):
                        population[idx] = new_scouts[k]

                # Stats y Logs
                for h in hofs: h.update(population)
                
                record = stats.compile(population)
                logbook.record(gen=cycle, evals=len(population)*2 + n_scouts, limit_hits=n_scouts, **record)
                printer.print(logbook.stream)
                
                # Feature Counts
                feature_names = collapsed_views.columns
                counts = [0] * len(feature_names)
                for ind in population:
                    if hasattr(ind, 'true_positions'): 
                        for pos in ind.true_positions():
                            counts[pos] += 1
                    else:
                        for idx, val in enumerate(ind):
                            if val: counts[idx] += 1
                feature_counts_saver.save(feature_counts=[counts], feature_names=feature_names)

            # --- RE-EVALUACIÓN FINAL (CRÍTICO) ---
            # 1. Extraemos las copias snapshot de los Hall of Fame
            hofs_snapshots = [h.hofers() for h in hofs]
            
            # 2. Recolectamos todos los individuos únicos
            all_hof_inds = []
            for snapshot in hofs_snapshots:
                all_hof_inds.extend(list(snapshot))
            
            # 3. Re-entrenamos CON PREDICTORES (keep_predictors=True)
            if all_hof_inds:
                # AQUÍ ES EL ÚNICO SITIO DONDE QUEREMOS MEMORIA GASTADA
                self._evaluate_population(evaluator, all_hof_inds, keep_predictors=True)
            
            # 4. Construimos el resultado usando las snapshots YA ACTUALIZADAS.
            final_results = hofers_to_results(hofs_snapshots)

        finally:
            evaluator.cleanup()

        logbook_saver.save(logbook)
        return final_results

    def _evaluate_population(self, evaluator, population, keep_predictors=False):
        """
        Evalúa la población y asigna FITNESS.
        
        OPTIMIZACIÓN DE RAM:
        Si keep_predictors=False (por defecto), eliminamos explícitamente la referencia 
        al modelo predictivo (RandomForest, etc.) para que el Garbage Collector lo libere.
        """
        if not population: return
        
        # evaluator.evaluate_batch devuelve una lista de objetos WorkerResult
        results = evaluator.evaluate_batch(population)
        
        for ind, res in zip(population, results):
            # 1. Asignar Fitness
            ind.fitness.values = res.fit()
            
            # 2. Gestión de Predictores (Modelos pesados)
            if keep_predictors:
                # Caso FINAL: Guardar el modelo real
                predictors_to_set = res.predictors()
            else:
                # Caso BUCLE: Guardar una lista de Nones para liberar RAM
                # Usamos len(res.fit()) para saber cuántos objetivos hay (ej: 2)
                # Creamos [None, None] para pasar la validación de longitud.
                n_objs = len(res.fit()) 
                predictors_to_set = [None] * n_objs

            if hasattr(ind, "set_predictors"):
                ind.set_predictors(predictors_to_set)
            else:
                ind.predictors = predictors_to_set

    def optimizer_type(self) -> MOOptimizerType:
        return self.__optimizer_type

    def name(self) -> str:
        return self.__name

    def nick(self) -> str:
        return self.__nick

    def __str__(self) -> str:
        res = ""
        res += name_value("Name", self.name()) + "\n"
        res += name_value("Nick", self.nick()) + "\n"
        res += name_value("Population size (Bees)", self.__pop_size) + "\n"
        res += name_value("Generations (Cycles)", self.__n_gen) + "\n"
        res += name_value("Scout Limit", self.__limit) + "\n"
        res += name_value("Initial features", self.__initial_features) + "\n"
        res += name_value("Mutation operator", self.__mutation) + "\n"
        res += name_value("Sorting strategy", self.__sorting_strategy) + "\n"
        return res