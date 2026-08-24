from abc import ABC, abstractmethod
import os

import numpy as np
import pandas as pd

from hyperparameter_evolution.log_float_hyperparameter import LogFloatHyperparameter
from hyperparameter_evolution.hyperparameter import Hyperparameter
from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from hyperparameter_evolution.integer_hyperparameter import IntegerHyperparameter
from hyperparameter_evolution.float_hyperparameter import FloatHyperparameter
from hyperparameter_evolution.categorical_hyperparameter import CategoricalHyperparameter
from hyperparameter_evolution.boolean_hyperparameter import BooleanHyperparameter

def order_df_columns( df: pd.DataFrame, ordered_columns: list = None, key=None ) -> pd.DataFrame:
    """
    Ordena las columnas de valores manteniendo 'gen'
    siempre como primera columna.

    Se puede ordenar:
    - Con un orden explícito mediante ordered_columns.
    - Mediante una función key.
    - Alfabéticamente si no se especifica ninguno.
    """

    value_columns = [
        column
        for column in df.columns
        if column != "gen"
    ]

    if ordered_columns is not None:
        value_columns = [
            column
            for column in ordered_columns
            if column in value_columns
        ]
    elif key is not None:
        value_columns = sorted(
            value_columns,
            key=key
        )
    else:
        value_columns = sorted(value_columns)

    return df[ ["gen"] + value_columns ]

def filter_generations( df: pd.DataFrame, save_interval: int ) -> pd.DataFrame:
    """
    Filtra las generaciones según save_interval y asegura que
    siempre se guarde la última generación.
    """

    if len(df) == 0:
        return df

    if save_interval <= 0:
        raise ValueError("save_interval debe ser mayor que 0")

    last_gen = df["gen"].iloc[-1]

    #Guarda los datos en intervalos y no todos
    return df[
        (df["gen"] % save_interval == 0)
        | (df["gen"] == last_gen)
    ]

def get_hyperparameter_values( hyperparameter_sets: list[HyperparameterSet], hyperparameter_nick: str ):
    """
    Funcion auxiliar para devolver los valores del hiperparametro especifico de la lista
    """
    return [
        hyperparameter_set.get(hyperparameter_nick).value()
        for hyperparameter_set in hyperparameter_sets
    ]

def hyperparameter_values_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int, sort_key=None) -> pd.DataFrame:
    """
    Cuenta los valores de un hiperparámetro en cada generación.

    Cada lista interna representa una generación y contiene los
    HyperparameterSet de todos los individuos de esa generación.
    """
    generations_counts = []
    for gen, hyperparameter_sets in enumerate(hyperparameter_counts):
        values = get_hyperparameter_values( hyperparameter_sets=hyperparameter_sets, hyperparameter_nick=hyperparameter_nick)
        counts = pd.Series(values).value_counts()
        counts["gen"] = gen
        generations_counts.append(counts)

    df = pd.DataFrame(generations_counts).fillna(0)

    gen_column = df.pop("gen")
    df.insert(0, "gen", gen_column)

    #Filtramos los intervalos
    df = filter_generations( df=df, save_interval=save_interval )

    df = order_df_columns( df=df, key=sort_key )

    return df

def hyperparameter_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int = 1) -> pd.DataFrame:
    """
    Convierte la evolución de un hiperparámetro concreto durante
    las generaciones del GA en un DataFrame.

    El tipo del DataFrame generado depende del tipo de Hyperparameter.
    """
    if len(hyperparameter_counts) == 0 or len(hyperparameter_counts[0]) == 0:
        return pd.DataFrame()

    first_hyperparameter = hyperparameter_counts[0][0].get( hyperparameter_nick )
    # Conteo de True y False
    if isinstance(first_hyperparameter, BooleanHyperparameter):
        return boolean_hyperparameter_counts_to_df( hyperparameter_counts=hyperparameter_counts,hyperparameter_nick=hyperparameter_nick, save_interval=save_interval )

    # Conteo de valores enteros
    if isinstance(first_hyperparameter, IntegerHyperparameter):
        return integer_hyperparameter_counts_to_df(hyperparameter_counts=hyperparameter_counts,hyperparameter_nick=hyperparameter_nick,save_interval=save_interval)

    # Conteo de categorias seleccionadas
    if isinstance(first_hyperparameter, CategoricalHyperparameter):
        return categorical_hyperparameter_counts_to_df(hyperparameter_counts=hyperparameter_counts,hyperparameter_nick=hyperparameter_nick,save_interval=save_interval)

    # Conteo de valores en rangos logarítmicos
    if isinstance(first_hyperparameter, LogFloatHyperparameter):
        return log_float_hyperparameter_counts_to_df( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, save_interval=save_interval )

    # Conteo de valores en rangos
    if isinstance(first_hyperparameter, FloatHyperparameter):
        return float_hyperparameter_counts_to_df(hyperparameter_counts=hyperparameter_counts,hyperparameter_nick=hyperparameter_nick,save_interval=save_interval)

    raise TypeError(
        f"Tipo de hiperparámetro no soportado: "
        f"{type(first_hyperparameter).__name__}"
    )

def boolean_hyperparameter_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int) -> pd.DataFrame:
    """
    Cuenta los valores True y False de un BooleanHyperparameter
    en cada generación.
    """
    return hyperparameter_values_counts_to_df( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, save_interval=save_interval, sort_key=lambda value: bool(value))

def integer_hyperparameter_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int ) -> pd.DataFrame:
    """
    Cuenta cada valor entero del hiperparámetro
    en cada generación.
    """
    return hyperparameter_values_counts_to_df( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, save_interval=save_interval, sort_key=lambda value: int(value))

def categorical_hyperparameter_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int ) -> pd.DataFrame:
    """
    Cuenta cada categoría seleccionada en cada generación.
    """
    return hyperparameter_values_counts_to_df(hyperparameter_counts=hyperparameter_counts,hyperparameter_nick=hyperparameter_nick,save_interval=save_interval, sort_key=lambda value: str(value))

def get_float_n_bins( lower_bound: float, upper_bound: float, target_bin_width: float = 0.1, max_bins: int = 20) -> int:
    """
    Funcion auxiliar para establecer el numero de cortes que recogera el csv con los datos float del hiperparametro
    """
    range_size = upper_bound - lower_bound

    if range_size <= 0:
        return 1

    return min(max_bins,max(1,int(np.ceil(range_size / target_bin_width))))

def float_hyperparameter_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int ) -> pd.DataFrame:
    """
    Cuenta los valores de un FloatHyperparameter por intervalos
    en cada generación.
    """

    first_hyperparameter = hyperparameter_counts[0][0].get( hyperparameter_nick )
    lower_bound = first_hyperparameter.lower_bound()
    upper_bound = first_hyperparameter.upper_bound()
    n_bins = get_float_n_bins( lower_bound=lower_bound, upper_bound=upper_bound )

    # Caso especial: solo existe un posible valor.
    if lower_bound == upper_bound:
        return hyperparameter_values_counts_to_df( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, save_interval=save_interval )

    # Creamos los mismos bins para todas las generaciones.
    bin_edges = np.linspace( lower_bound, upper_bound, n_bins + 1 )

    bin_labels = [
        f"[{bin_edges[i]:.6g}, {bin_edges[i + 1]:.6g}]"
        for i in range(n_bins)
    ]

    generations_counts = []
    for gen, hyperparameter_sets in enumerate(hyperparameter_counts):
        # Obtenemos los valores de todos los individuos de esta generación.
        values = get_hyperparameter_values(
            hyperparameter_sets=hyperparameter_sets,
            hyperparameter_nick=hyperparameter_nick
        )

        # Asignamos cada valor a un bin.
        binned_values = pd.cut(values,bins=bin_edges,labels=bin_labels,include_lowest=True)

        # Contamos los individuos de cada bin.
        counts = pd.Series(binned_values).value_counts()

        # Guardamos la generación.
        counts["gen"] = gen
        generations_counts.append(counts)

    # Convertimos todas las generaciones a un DataFrame.
    df = pd.DataFrame(generations_counts).fillna(0)
    df = df.reindex( columns=["gen"] + bin_labels, fill_value=0 )

    # Movemos "gen" a la primera columna.
    gen_column = df.pop("gen")
    df.insert(0, "gen", gen_column)

    #filtrar los intervalo acordados
    df = filter_generations( df=df, save_interval=save_interval )

    # Ordenamos los intervalos según el orden numérico en el que fueron creados.
    df = order_df_columns( df=df, ordered_columns=bin_labels )
    df = df.astype(int)

    return df

def get_log_float_n_bins( log_lower_bound: float, log_upper_bound: float, bins_per_order: int = 1, max_bins: int = 20 ) -> int:
    """
    Funcion auxiliar para establecer el numero de cortes que recogera el csv con los datos log del hiperparametro
    """
    log_range = log_upper_bound - log_lower_bound
    if log_range <= 0:
        return 1

    return min( max_bins, max(1, int(np.ceil(log_range * bins_per_order))) )

def log_float_hyperparameter_counts_to_df( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, save_interval: int ) -> pd.DataFrame:
    """
    Cuenta los valores de un LogFloatHyperparameter utilizando
    intervalos uniformes en escala log10.
    """

    first_hyperparameter = hyperparameter_counts[0][0].get( hyperparameter_nick )
    lower_bound = first_hyperparameter.lower_bound()
    upper_bound = first_hyperparameter.upper_bound()

    if lower_bound <= 0 or upper_bound <= 0:
        raise ValueError( "Los límites de un LogFloatHyperparameter deben ser mayores que 0" )

    # Caso especial: solo existe un posible valor.
    if lower_bound == upper_bound:
        return hyperparameter_values_counts_to_df( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, save_interval=save_interval)

    # Pasamos los límites a escala log10.
    log_lower_bound = np.log10(lower_bound)
    log_upper_bound = np.log10(upper_bound)

    # Número de bins según el número de órdenes de magnitud.
    n_bins = get_log_float_n_bins( log_lower_bound=log_lower_bound, log_upper_bound=log_upper_bound )

    # Creamos bins uniformes en el espacio logarítmico.
    log_bin_edges = np.linspace( log_lower_bound, log_upper_bound, n_bins + 1 )

    # Convertimos los bordes de nuevo a escala real.
    bin_edges = 10 ** log_bin_edges

    bin_labels = [
        f"[{bin_edges[i]:.6g}, {bin_edges[i + 1]:.6g}]"
        for i in range(n_bins)
    ]

    generations_counts = []

    for gen, hyperparameter_sets in enumerate(hyperparameter_counts):
        values = get_hyperparameter_values( hyperparameter_sets=hyperparameter_sets, hyperparameter_nick=hyperparameter_nick )
        binned_values = pd.cut( values, bins=bin_edges, labels=bin_labels, include_lowest=True )
        counts = pd.Series(binned_values).value_counts()
        counts["gen"] = gen
        generations_counts.append(counts)

    df = pd.DataFrame(generations_counts).fillna(0)
    df = df.reindex( columns=["gen"] + bin_labels, fill_value=0 )

    gen_column = df.pop("gen")
    df.insert(0, "gen", gen_column)

    #filtrar los intervalo acordados
    df = filter_generations( df=df, save_interval=save_interval )

    # Los bins ya están creados de menor a mayor  en escala logarítmica.
    df = order_df_columns( df=df, ordered_columns=bin_labels )
    df = df.astype(int)

    return df

def hyperparameter_counts_to_csv( hyperparameter_counts: list[list[HyperparameterSet]], hyperparameter_nick: str, file: str, save_interval: int = 1 ):
    """
    Convierte la evolución de un hiperparámetro a un archivo CSV.
    """
    df_counts = hyperparameter_counts_to_df( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, save_interval=save_interval )
    df_counts.to_csv(file, index=False)


class HyperparameterCountsSaver(ABC):
    """
    Clase base encargada de definir un método de guardado
    permanente de datos de evolución de HyperparameterSet.
    """

    @abstractmethod
    def save(self,hyperparameter_counts: list[list[HyperparameterSet]]):
        raise NotImplementedError()


class DummyHyperparameterCountsSaver(HyperparameterCountsSaver):
    def save( self,hyperparameter_counts: list[list[HyperparameterSet]]):
        pass


class CsvHyperparameterCountsSaver(HyperparameterCountsSaver):
    """
    Clase encargada de almacenar la evolución de los hiperparámetros
    en archivos CSV.
    """
    __directory: str
    __complement: str
    __save_interval: int

    def __init__(self,directory: str,complement: str,save_interval: int = 1):
        self.__directory = directory
        self.__complement = complement
        self.__save_interval = save_interval

    def save(self,hyperparameter_counts: list[list[HyperparameterSet]]):
        if len(hyperparameter_counts) == 0:
            return

        if len(hyperparameter_counts[0]) == 0:
            return

        os.makedirs(self.__directory,exist_ok=True)
        first_hyperparameter_set = hyperparameter_counts[0][0]
        for hyperparameter in first_hyperparameter_set.values():
            #Si no es mutable no nos interesa guardarlo
            if not hyperparameter.mutable():
                continue
            hyperparameter_nick = hyperparameter.nick()
            file = os.path.join( self.__directory, f"hyperparameter_counts_" f"{hyperparameter_nick}_" f"{self.__complement}.csv" )
            hyperparameter_counts_to_csv( hyperparameter_counts=hyperparameter_counts, hyperparameter_nick=hyperparameter_nick, file=file, save_interval=self.__save_interval)