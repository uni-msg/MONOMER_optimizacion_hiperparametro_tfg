import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import DataFrame

from consts import GEN_STR, HYPERPARAMETER_COUNTS_PATH
from cross_validation.multi_objective.cross_evaluator.feature_stability_mo_cross_eval import stability_by_weights_from_counts
from util.hyperparameter_plot import create_plot_directory
from util.sequence_utils import stable_uniques


HYPERPARAMETER_COUNTS_PREFIX = "hyperparameter_counts_"
HYPERPARAMETER_COUNTS_EXTENSION = "csv"
FOLD_STRING = "_fold_"


def merge_df(dfs: list[DataFrame], sort=False) -> DataFrame:
    """
    Agrupa los DataFrames concatenando por filas.

    Cada fila resultante representa los conteos
    de un fold en una generación concreta.
    """
    #Une todos los DataFrames manteniendo todas las columnas disponibles
    merged_df = pd.concat(dfs, axis=0, ignore_index=True, join="outer", sort=sort)

    #Sustituye los valores ausentes por 0
    return merged_df.fillna(0)


def generations_and_hyperparameter_columns(merged_df: DataFrame) -> tuple[list, list[str]]:
    """
    Obtiene las generaciones y las columnas que
    representan los valores del hiperparámetro.
    """
    #Obtiene las generaciones manteniendo el orden original
    gens = stable_uniques(merged_df[GEN_STR])

    #Obtiene las columnas que representan los valores del hiperparámetro
    hyperparameter_columns = [
        column
        for column in merged_df.columns
        if column != GEN_STR
    ]

    return gens, hyperparameter_columns


def valid_folds_dfs(dfs: list[DataFrame]) -> bool:
    """
    Comprueba si existen suficientes folds para
    comparar y si contienen la columna de generación.
    """
    #Se necesitan al menos dos folds para comparar
    if len(dfs) <= 1:
        return False

    #Comprueba que los DataFrames contienen la columna de generación
    if GEN_STR not in dfs[0].columns:
        return False

    return True


def common_hyperparameter_values_between_folds(merged_df: DataFrame) -> DataFrame:
    """
    Calcula, para cada generación y cada rango
    del hiperparámetro, el número de folds en los
    que dicho rango está activo.

    Cada fila representa una generación.
    Cada columna representa un rango del hiperparámetro.

    El valor de cada celda indica el número de
    folds que utilizaron ese rango.
    """
    gens, hyperparameter_columns = generations_and_hyperparameter_columns(merged_df=merged_df)

    common_values = []

    #Analiza cada generación por separado
    for gen in gens:
        #Obtiene los conteos de todos los folds para la generación actual
        row_counts = merged_df.loc[merged_df[GEN_STR] == gen, hyperparameter_columns]

        #Cuenta en cuántos folds está activo cada valor del hiperparámetro
        active_folds_per_hyperparameter = (row_counts != 0).sum(axis=0)

        #Guarda el resultado de la generación
        common_values.append(active_folds_per_hyperparameter.to_dict())

    #Convierte los resultados en un DataFrame
    common_values_df = DataFrame(common_values, index=gens)
    common_values_df.index.name = GEN_STR

    return common_values_df


def stability_of_weights_between_folds(merged_df: DataFrame) -> DataFrame:
    """
    Calcula la estabilidad por pesos para cada
    generación y cada rango del hiperparámetro.

    Para cada fold, el peso de un rango se calcula como:

        conteo_del_rango / suma_de_todos_los_conteos_del_fold

    Después, para cada rango, se mide la estabilidad
    entre folds como:

        mínimo_peso / máximo_peso

    Por tanto:

        1.0 -> el rango tiene exactamente el mismo peso en todos los folds.
        0.0 -> el rango no se utiliza en algún fold y sí en otro.
        valores intermedios -> existen diferencias en su utilización.
    """
    gens, hyperparameter_columns = generations_and_hyperparameter_columns(merged_df=merged_df)

    stability_by_generation = []

    #Calcula la estabilidad para cada generación
    for gen in gens:
        #Obtiene los conteos de todos los folds para la generación actual
        row_counts = merged_df.loc[merged_df[GEN_STR] == gen, hyperparameter_columns].copy()

        #Calcula el número total de usos del hiperparámetro en cada fold
        fold_totals = row_counts.sum(axis=1)

        #Normaliza los conteos para obtener los pesos relativos de cada rango
        normalized_weights = row_counts.div(fold_totals.replace(0, 1), axis=0)

        generation_stability = {}

        #Calcula la estabilidad de cada valor del hiperparámetro
        for hyperparameter_value in hyperparameter_columns:
            weights = normalized_weights[hyperparameter_value]

            max_weight = weights.max()
            min_weight = weights.min()

            #Si ningún fold utiliza el valor, se considera completamente estable
            if max_weight == 0:
                stability = 1.0
            else:
                #Compara el menor peso con el mayor peso entre folds
                stability = min_weight / max_weight

            generation_stability[hyperparameter_value] = stability

        #Guarda la estabilidad de todos los valores de la generación
        stability_by_generation.append(generation_stability)

    #Convierte los resultados en un DataFrame
    stability_df = DataFrame(stability_by_generation, index=gens)
    stability_df.index.name = GEN_STR

    return stability_df


def stability_of_unions_between_folds(merged_df: DataFrame) -> DataFrame:
    """
    Calcula la estabilidad por unión para cada
    generación y cada rango del hiperparámetro.

    Para un rango concreto:

        estabilidad = número de folds en los que está activo
                      --------------------------------------
                              número total de folds

    Por tanto:

        1.0 -> activo en todos los folds.
        0.0 -> no está activo en ningún fold.
        0.5 -> activo en la mitad de los folds.
    """
    gens, hyperparameter_columns = generations_and_hyperparameter_columns(merged_df=merged_df)

    stability_by_generation = []

    #Calcula la estabilidad para cada generación
    for gen in gens:
        #Obtiene los conteos de todos los folds para la generación actual
        row_counts = merged_df.loc[merged_df[GEN_STR] == gen, hyperparameter_columns]

        #Obtiene el número de folds disponibles para la generación
        number_of_folds = len(row_counts)

        generation_stability = {}

        #Calcula la proporción de folds que utilizan cada valor
        for hyperparameter_value in hyperparameter_columns:
            active_folds = (row_counts[hyperparameter_value] != 0).sum()

            #Evita divisiones por cero
            if number_of_folds == 0:
                stability = 0.0
            else:
                stability = active_folds / number_of_folds

            generation_stability[hyperparameter_value] = stability

        #Guarda la estabilidad de todos los valores de la generación
        stability_by_generation.append(generation_stability)

    #Convierte los resultados en un DataFrame
    stability_df = DataFrame(stability_by_generation, index=gens)
    stability_df.index.name = GEN_STR

    return stability_df


def hyperparameter_global_stability_between_folds(merged_df: DataFrame) -> tuple[list, list[float]]:
    """
    Calcula la estabilidad global del hiperparámetro
    entre folds para cada generación.

    Para cada generación:

    1. Cada fila representa la distribución de uso
       de todos los rangos del hiperparámetro en un fold.

    2. La distribución de cada fold se normaliza para
       que sus pesos sumen 1.

    3. Se calcula la estabilidad global entre las
       distribuciones de todos los folds utilizando
       exactamente la misma métrica empleada en la
       estabilidad por pesos de las features.

    Por tanto, esta función no mide la estabilidad de
    un rango concreto, sino la estabilidad de la
    distribución completa del hiperparámetro.

    Devuelve:
        - Lista de generaciones.
        - Lista de valores de estabilidad global.
    """
    gens, hyperparameter_columns = generations_and_hyperparameter_columns(merged_df=merged_df)

    stability = []

    #Calcula un único valor global de estabilidad para cada generación
    for gen in gens:
        #Obtiene la distribución completa del hiperparámetro en todos los folds
        row_counts = merged_df.loc[merged_df[GEN_STR] == gen, hyperparameter_columns]

        #Calcula la estabilidad utilizando la misma métrica que para las features
        stability.append(stability_by_weights_from_counts(row_counts.values.tolist()))

    return gens, stability


def common_hyperparameter_values_df_to_plot(plot_dir: str, plot_name: str, common_values_df: DataFrame):
    """
    Crea un mapa de calor que muestra para cada
    generación y cada rango del hiperparámetro el
    número de folds en los que dicho rango está activo.
    """
    #Crea la figura del mapa de calor
    fig, ax = plt.subplots(figsize=(20, 15))

    #Representa el número de folds que utilizan cada valor
    sns.heatmap(common_values_df, annot=True, fmt=".0f", ax=ax)

    #Configura las etiquetas de los ejes
    ax.set_xlabel("Hyperparameter values")
    ax.set_ylabel("Generation")

    #Guarda la figura
    plt.savefig(os.path.join(plot_dir, plot_name), dpi=600, bbox_inches="tight")

    #Cierra la figura para liberar recursos
    plt.close(fig)


def stability_between_folds_df_to_plot(plot_dir: str, plot_name: str, stability_df: DataFrame, x_label: str):
    """
    Crea un mapa de calor con la estabilidad entre
    folds para cada generación y cada rango del
    hiperparámetro.
    """
    #Crea la figura del mapa de calor
    fig, ax = plt.subplots(figsize=(20, 15))

    #Representa los valores de estabilidad entre 0 y 1
    sns.heatmap(stability_df, annot=True, fmt=".4f", ax=ax, vmin=0, vmax=1)

    #Configura las etiquetas de los ejes
    ax.set_xlabel(x_label)
    ax.set_ylabel("Generation")

    #Guarda la figura
    plt.savefig(os.path.join(plot_dir, plot_name), dpi=600, bbox_inches="tight")

    #Cierra la figura para liberar recursos
    plt.close(fig)


def hyperparameter_global_stability_plot(generations: list, stability: list[float], plot_dir: str, plot_name: str):
    """
    Crea una gráfica lineal de la estabilidad
    global del hiperparámetro entre folds.

    El eje X representa las generaciones.

    El eje Y representa la similitud global de las
    distribuciones de valores del hiperparámetro
    entre folds.

    1.0 representa máxima estabilidad.
    0.0 representa mínima estabilidad.
    """
    #Crea la figura y los ejes
    fig, ax = plt.subplots()

    #Configura los ejes
    ax.set_xlabel("Generation")
    ax.set_ylabel("Stability of folds")
    ax.set_ylim(0, 1)

    #Representa la estabilidad global a lo largo de las generaciones
    lines = ax.plot(generations, stability, "b-", label="Stability of folds")

    #Obtiene las etiquetas de las líneas
    labels = [line.get_label() for line in lines]

    #Añade la leyenda
    ax.legend(lines, labels, loc="center right")

    #Guarda la figura
    plt.savefig(os.path.join(plot_dir, plot_name), bbox_inches="tight", dpi=600)

    #Cierra la figura para liberar recursos
    plt.close(fig)


def dfs_to_common_hyperparameter_values_between_folds_plot(dfs: list[DataFrame], plot_dir: str, hyperparameter_name: str):
    """
    Calcula y representa mediante un mapa de calor
    los rangos de valores del hiperparámetro utilizados
    por los diferentes folds en cada generación.
    """
    #Comprueba que existen suficientes folds válidos
    if not valid_folds_dfs(dfs=dfs):
        return

    #Une los resultados de todos los folds
    merged_df = merge_df(dfs=dfs)

    #Calcula el número de folds que utilizan cada valor
    common_values_df = common_hyperparameter_values_between_folds(merged_df=merged_df)

    #Crea el mapa de calor
    common_hyperparameter_values_df_to_plot(
        plot_dir=plot_dir,
        plot_name="common_hyperparameter_values_between_folds_" + hyperparameter_name + ".png",
        common_values_df=common_values_df
    )


def dfs_to_hyperparameter_stability_between_folds_plots(dfs: list[DataFrame], plot_dir: str, hyperparameter_name: str):
    """
    Calcula dos mapas de calor para cada hiperparámetro:

    1. Estabilidad por pesos:
       Para cada generación y rango muestra cómo
       de parecido es su peso relativo entre folds.

    2. Estabilidad por unión:
       Para cada generación y rango muestra en qué
       proporción de folds dicho rango está activo.
    """
    #Comprueba que existen suficientes folds válidos
    if not valid_folds_dfs(dfs=dfs):
        return

    #Une los resultados de todos los folds
    merged_df = merge_df(dfs=dfs)

    #Calcula la estabilidad basada en los pesos relativos
    weights_stability_df = stability_of_weights_between_folds(merged_df=merged_df)

    #Crea el mapa de calor de estabilidad por pesos
    stability_between_folds_df_to_plot(
        plot_dir=plot_dir,
        plot_name="hyperparameter_stability_of_weights_between_folds_" + hyperparameter_name + ".png",
        stability_df=weights_stability_df,
        x_label="Hyperparameter values"
    )

    #Calcula la estabilidad basada en la proporción de folds activos
    unions_stability_df = stability_of_unions_between_folds(merged_df=merged_df)

    #Crea el mapa de calor de estabilidad por unión
    stability_between_folds_df_to_plot(
        plot_dir=plot_dir,
        plot_name="hyperparameter_stability_of_unions_between_folds_" + hyperparameter_name + ".png",
        stability_df=unions_stability_df,
        x_label="Hyperparameter values"
    )


def dfs_to_hyperparameter_global_stability_between_folds_plot(dfs: list[DataFrame], plot_dir: str, hyperparameter_name: str):
    """
    Genera una gráfica lineal con la estabilidad
    global del hiperparámetro entre folds.

    Es conceptualmente equivalente a la gráfica
    lineal de estabilidad entre folds utilizada
    para las features.

    Para cada generación se compara la distribución
    completa de rangos del hiperparámetro de todos
    los folds.

    No analiza los rangos individualmente. Produce
    un único valor global de estabilidad por generación.
    """
    #Comprueba que existen suficientes folds válidos
    if not valid_folds_dfs(dfs=dfs):
        return

    #Une los resultados de todos los folds
    merged_df = merge_df(dfs=dfs)

    #Calcula la estabilidad global para cada generación
    generations, stability = hyperparameter_global_stability_between_folds(merged_df=merged_df)

    #Crea la gráfica lineal de estabilidad global
    hyperparameter_global_stability_plot(
        generations=generations,
        stability=stability,
        plot_dir=plot_dir,
        plot_name="hyperparameter_stability_between_folds_" + hyperparameter_name + ".png"
    )


def hyperparameter_name_from_file(file: str) -> str:
    """
    Extrae el nombre del hiperparámetro.

    Ejemplo:

        hyperparameter_counts_var_smoothing_fold_0.csv -> var_smoothing
    """
    #Elimina el prefijo del nombre del archivo
    file_without_prefix = file[len(HYPERPARAMETER_COUNTS_PREFIX):]

    #El nombre se encuentra antes de la parte correspondiente al fold
    return file_without_prefix.split(FOLD_STRING)[0]


def is_hyperparameter_counts_file(file: str) -> bool:
    """
    Comprueba si un archivo corresponde a los
    conteos de un hiperparámetro.
    """
    return file.startswith(HYPERPARAMETER_COUNTS_PREFIX) and file.endswith("." + HYPERPARAMETER_COUNTS_EXTENSION)


def load_saved_hyperparameter_counts(direct: str) -> dict[str, list[DataFrame]]:
    """
    Carga los archivos de conteo de hiperparámetros
    agrupándolos por nombre del hiperparámetro.
    """
    hyperparameter_dfs = {}

    #Obtiene y ordena todos los archivos del directorio
    files = sorted(os.listdir(direct))

    #Recorre los archivos de conteo de hiperparámetros
    for file in files:
        #Ignora los archivos que no corresponden a conteos de hiperparámetros
        if not is_hyperparameter_counts_file(file=file):
            continue

        #Obtiene el nombre del hiperparámetro correspondiente al archivo
        hyperparameter_name = hyperparameter_name_from_file(file=file)

        #Inicializa la lista del hiperparámetro cuando aparece por primera vez
        if hyperparameter_name not in hyperparameter_dfs:
            hyperparameter_dfs[hyperparameter_name] = []

        #Lee el CSV y lo añade a la lista de folds del hiperparámetro
        hyperparameter_dfs[hyperparameter_name].append(
            pd.read_csv(filepath_or_buffer=os.path.join(direct, file))
        )

    return hyperparameter_dfs


def hyperparameter_diversity_plots_for_directory(direct: str):
    """
    Genera tres gráficas para cada hiperparámetro:

    1. Estabilidad por pesos:
       Heatmap que muestra, para cada generación y
       rango, cómo de parecido es su peso relativo
       entre folds.

    2. Estabilidad por unión:
       Heatmap que muestra, para cada generación y
       rango, en qué proporción de folds está activo.

    3. Estabilidad global entre folds:
       Gráfica lineal que muestra, para cada generación,
       cómo de parecidas son las distribuciones completas
       del hiperparámetro entre todos los folds.
    """
    #Construye el directorio donde se encuentran los conteos de hiperparámetros
    hyperparameter_counts_dir = direct + HYPERPARAMETER_COUNTS_PATH

    #Crea el directorio de salida si no existe
    create_plot_directory(directory=hyperparameter_counts_dir)

    #Carga los conteos agrupados por hiperparámetro
    hyperparameter_dfs = load_saved_hyperparameter_counts(direct=hyperparameter_counts_dir)

    #Procesa los resultados de cada hiperparámetro
    for hyperparameter_name, dfs in hyperparameter_dfs.items():
        #Se necesitan al menos dos folds para calcular estabilidad
        if len(dfs) <= 1:
            continue

        #Crea las gráficas de estabilidad por pesos y por unión
        dfs_to_hyperparameter_stability_between_folds_plots(
            dfs=dfs,
            plot_dir=hyperparameter_counts_dir,
            hyperparameter_name=hyperparameter_name
        )

        #Crea la gráfica de estabilidad global entre folds
        dfs_to_hyperparameter_global_stability_between_folds_plot(
            dfs=dfs,
            plot_dir=hyperparameter_counts_dir,
            hyperparameter_name=hyperparameter_name
        )