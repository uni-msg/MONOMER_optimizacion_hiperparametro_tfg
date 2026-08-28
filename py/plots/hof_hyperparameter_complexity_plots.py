import os

import pandas as pd
from pandas import DataFrame

from util.hyperparameter_plot import (
    create_plot_directory,
    final_file_by_prefix,
    fold_files_by_prefix,
    hof_subdirectories,
    hyperparameter_values_are_constant,
    hyperparameters_final_file,
    hyperparameters_fold_files,
    read_hyperparameters
)
from util.hyperparameter_plot_results import save_hyperparameter_multiclass_scatter


HYPERPARAMETERS_DIR = "hyperparameters"
SOLUTION_FEATURES_PREFIX = "solution_features"


def features_fold_files(hof_dir: str) -> dict[int, str]:
    """
    Obtiene los archivos de features indexados por número de fold.
    """
    return fold_files_by_prefix(directory=hof_dir, prefix=SOLUTION_FEATURES_PREFIX)


def features_final_file(hof_dir: str):
    """
    Obtiene el archivo final de features.

    Soporta:

        solution_features_final.csv

    y:

        solution_features_fold_final.csv
    """
    #Busca primero el archivo final con el nombre normal
    file_path = final_file_by_prefix(directory=hof_dir, prefix=SOLUTION_FEATURES_PREFIX)

    if file_path is not None:
        return file_path

    #Comprueba el nombre alternativo utilizado por algunos resultados
    alternative_file_path = os.path.join(hof_dir, SOLUTION_FEATURES_PREFIX + "_fold_final.csv")

    if os.path.isfile(alternative_file_path):
        return alternative_file_path

    return None


def read_features(file_path: str) -> DataFrame:
    """
    Lee un archivo CSV de features seleccionadas.
    """
    return pd.read_csv(file_path)


def solution_complexities(features_df: DataFrame) -> list[int]:
    """
    Calcula la complejidad de cada solución.

    La complejidad se define como el número de features seleccionadas.

    Una feature seleccionada se representa con:

        1

    Una feature no seleccionada se representa con:

        0

    Por lo tanto, para cada solución:

        complejidad =
            número de features seleccionadas
    """
    #Convierte todos los valores a numéricos y los valores no válidos a NaN
    numeric_features_df = features_df.apply(pd.to_numeric, errors="coerce")

    #Cuenta las features seleccionadas de cada solución
    return numeric_features_df.eq(1).sum(axis=1).astype(int).tolist()


def plot_hyperparameter_vs_complexity(hyperparameter_values, complexities: list[int], save_file: str, hyperparameter_name: str):
    """
    Crea una gráfica de:

        hiperparámetro
            vs
        complejidad de la solución

    La complejidad es el número de features seleccionadas.

    El eje X es seleccionado automáticamente por save_hyperparameter_multiclass_scatter:

        - categórico
        - entero
        - float
        - logarítmico cuando sea apropiado

    Los hiperparámetros constantes se ignoran.
    """
    #No tiene sentido crear una gráfica sin valores
    if len(hyperparameter_values) == 0:
        return

    #Ignora los hiperparámetros que no presentan variación
    if hyperparameter_values_are_constant(hyperparameter_values=hyperparameter_values):
        return

    #Cada valor del hiperparámetro debe tener una complejidad asociada
    if len(hyperparameter_values) != len(complexities):
        raise ValueError(
            "Different number of hyperparameter values and complexity values for "
            f"hyperparameter '{hyperparameter_name}'. Hyperparameters: {len(hyperparameter_values)}. "
            f"Complexities: {len(complexities)}."
        )

    #Crea la gráfica utilizando una única clase llamada solutions
    save_hyperparameter_multiclass_scatter(
        x=[hyperparameter_values],
        y=[complexities],
        save_file=save_file,
        x_label=hyperparameter_name,
        y_label="number of selected features",
        class_labels=["solutions"]
    )


def union_hyperparameters_vs_complexity_plots(hyperparameters_dfs: list[DataFrame], features_dfs: list[DataFrame], plot_dir: str):
    """
    Crea una gráfica de Hyperparameter vs complexity para cada hiperparámetro no constante.

    Se unen todas las soluciones de todos los folds.

    La solución final no se incluye.
    """
    #Si no existen resultados, no hay nada que representar
    if len(hyperparameters_dfs) == 0:
        return

    #Debe existir un dataframe de features por cada dataframe de hiperparámetros
    if len(hyperparameters_dfs) != len(features_dfs):
        raise ValueError("Different number of hyperparameters and features dataframes.")

    first_hyperparameters_df = hyperparameters_dfs[0]

    #Recorre todos los hiperparámetros disponibles
    for hyperparameter_name in first_hyperparameters_df.columns:
        union_hyperparameter_values = []
        union_complexities = []

        #Recorre los resultados de todos los folds
        for (hyperparameters_df, features_df) in zip(hyperparameters_dfs, features_dfs):
            #Todos los folds deben contener el mismo hiperparámetro
            if hyperparameter_name not in hyperparameters_df.columns:
                raise ValueError("Hyperparameter '" + hyperparameter_name + "' is not present in every fold.")

            #Obtiene los valores del hiperparámetro para el fold actual
            hyperparameter_values = hyperparameters_df[hyperparameter_name].tolist()

            #Calcula la complejidad de cada solución del fold
            complexities = solution_complexities(features_df=features_df)

            #Comprueba que cada solución de hiperparámetros tenga sus features correspondientes
            if len(hyperparameter_values) != len(complexities):
                raise ValueError(
                    "Different number of hyperparameter values and feature solutions in one "
                    f"fold for hyperparameter '{hyperparameter_name}'. Hyperparameters: "
                    f"{len(hyperparameter_values)}. Feature solutions: {len(complexities)}."
                )

            #Añade los valores del fold a la unión
            union_hyperparameter_values.extend(hyperparameter_values)
            union_complexities.extend(complexities)

        #No representa hiperparámetros constantes
        if hyperparameter_values_are_constant(hyperparameter_values=union_hyperparameter_values):
            continue

        #Construye el nombre del archivo de salida
        save_file = os.path.join(plot_dir, hyperparameter_name + "_complexity.png")

        #Crea la gráfica utilizando todos los folds unidos
        plot_hyperparameter_vs_complexity(
            hyperparameter_values=union_hyperparameter_values,
            complexities=union_complexities,
            save_file=save_file,
            hyperparameter_name=hyperparameter_name
        )


def final_hyperparameters_vs_complexity_plots(hyperparameters_file: str, features_file: str, plot_dir: str):
    """
    Crea una gráfica de Hyperparameter vs complexity para cada hiperparámetro no constante utilizando las soluciones finales.
    """
    #Lee los hiperparámetros y features de las soluciones finales
    hyperparameters_df = read_hyperparameters(file_path=hyperparameters_file)
    features_df = read_features(file_path=features_file)

    #Calcula la complejidad de las soluciones finales
    complexities = solution_complexities(features_df=features_df)

    #Crea una gráfica para cada hiperparámetro
    for hyperparameter_name in hyperparameters_df.columns:
        hyperparameter_values = hyperparameters_df[hyperparameter_name].tolist()

        #Construye el nombre del archivo de salida
        save_file = os.path.join(plot_dir, hyperparameter_name + "_complexity_final.png")

        #Crea la gráfica del hiperparámetro frente a la complejidad
        plot_hyperparameter_vs_complexity(
            hyperparameter_values=hyperparameter_values,
            complexities=complexities,
            save_file=save_file,
            hyperparameter_name=hyperparameter_name
        )


def hof_hyperparameter_complexity_plots_for_directory(hof_dir: str):
    """
    Crea gráficas de Hyperparameter vs complexity para un directorio Hall Of Fame.

    Archivos esperados:

        solution_hyperparameters_fold_0.csv
        solution_features_fold_0.csv

        solution_hyperparameters_fold_1.csv
        solution_features_fold_1.csv

        ...

    Archivos finales:

        solution_hyperparameters_final.csv

    y uno de:

        solution_features_final.csv
        solution_features_fold_final.csv

    La complejidad se calcula como el número de features seleccionadas.

    Salida:

        hof_dir/hyperparameters/
    """
    #Crea el directorio donde se guardarán las gráficas
    plot_dir = create_plot_directory(directory=os.path.join(hof_dir, HYPERPARAMETERS_DIR))

    #Obtiene los archivos de hiperparámetros y features de todos los folds
    hyperparameters_files_by_fold = hyperparameters_fold_files(hof_dir=hof_dir)
    features_files_by_fold = features_fold_files(hof_dir=hof_dir)

    #Busca los folds que contienen ambos archivos
    common_folds = sorted(
        set(hyperparameters_files_by_fold.keys())
        & set(features_files_by_fold.keys())
    )

    hyperparameters_dfs = []
    features_dfs = []

    #Lee los resultados de todos los folds comunes
    for fold_number in common_folds:
        hyperparameters_file = hyperparameters_files_by_fold[fold_number]
        features_file = features_files_by_fold[fold_number]

        hyperparameters_dfs.append(read_hyperparameters(file_path=hyperparameters_file))
        features_dfs.append(read_features(file_path=features_file))

    #Crea las gráficas utilizando la unión de todos los folds
    union_hyperparameters_vs_complexity_plots(
        hyperparameters_dfs=hyperparameters_dfs,
        features_dfs=features_dfs,
        plot_dir=plot_dir
    )

    #Busca los archivos de las soluciones finales
    final_hyperparameters_file = hyperparameters_final_file(hof_dir=hof_dir)
    final_features_file = features_final_file(hof_dir=hof_dir)

    #Si existen ambos archivos finales, crea las gráficas finales
    if final_hyperparameters_file is not None and final_features_file is not None:
        final_hyperparameters_vs_complexity_plots(
            hyperparameters_file=final_hyperparameters_file,
            features_file=final_features_file,
            plot_dir=plot_dir
        )


def hof_hyperparameter_complexity_plots_every_hof(main_hofs_dir: str):
    """
    Crea gráficas de Hyperparameter vs complexity para todos los directorios Hall Of Fame.
    """
    #Obtiene todos los subdirectorios que representan un Hall Of Fame
    for hof_dir in hof_subdirectories(main_hofs_dir=main_hofs_dir):
        #Procesa cada Hall Of Fame individualmente
        hof_hyperparameter_complexity_plots_for_directory(hof_dir=hof_dir)