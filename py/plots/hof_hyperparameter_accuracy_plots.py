import os
from typing import Optional

import pandas as pd
from pandas import DataFrame

from util.hyperparameter_plot import (
    SOLUTION_HYPERPARAMETERS_PREFIX,
    create_plot_directory,
    final_file_by_prefix,
    fold_files_by_prefix,
    hof_subdirectories,
    hyperparameters_final_file,
    hyperparameters_fold_files,
    read_hyperparameters
)
from util.hyperparameter_plot_results import save_hyperparameter_multiclass_scatter


HYPERPARAMETERS_DIR = "hyperparameters"

SOLUTION_FITNESSES_PREFIX = "solution_fitnesses"

INNER_CV_PREFIX = "inner_cv__"
TRAIN_PREFIX = "train_"
TEST_PREFIX = "test_"

BALANCED_ACCURACY_SUFFIX = "_bal_acc"


def fitnesses_fold_files(hof_dir: str) -> dict[int, str]:
    """
    Obtiene los archivos de fitness de cada fold
    indexados por su numero de fold.
    """
    return fold_files_by_prefix(directory=hof_dir, prefix=SOLUTION_FITNESSES_PREFIX)


def fitnesses_final_file(hof_dir: str) -> Optional[str]:
    """
    Obtiene el archivo final de fitness
    si existe.
    """
    return final_file_by_prefix(directory=hof_dir, prefix=SOLUTION_FITNESSES_PREFIX)


def read_fitnesses(file_path: str) -> DataFrame:
    """
    Lee un archivo CSV de fitness y
    devuelve su contenido como un DataFrame.
    """
    return pd.read_csv(file_path)


def balanced_accuracy_column(df: DataFrame, prefix: str) -> Optional[str]:
    """
    Busca la columna de balanced accuracy
    correspondiente al prefijo indicado.
    """
    #Recorre todas las columnas del DataFrame
    for column in df.columns:
        #Busca la columna con el prefijo y sufijo esperados
        if column.startswith(prefix) and column.endswith(BALANCED_ACCURACY_SUFFIX):
            return column

    return None


def inner_cv_balanced_accuracy_column(df: DataFrame) -> Optional[str]:
    """
    Busca la columna de balanced accuracy
    correspondiente al inner CV.
    """
    return balanced_accuracy_column(df=df, prefix=INNER_CV_PREFIX)


def train_balanced_accuracy_column(df: DataFrame) -> Optional[str]:
    """
    Busca la columna de balanced accuracy
    correspondiente al train.
    """
    return balanced_accuracy_column(df=df, prefix=TRAIN_PREFIX)


def test_balanced_accuracy_column(df: DataFrame) -> Optional[str]:
    """
    Busca la columna de balanced accuracy
    correspondiente al test.
    """
    return balanced_accuracy_column(df=df, prefix=TEST_PREFIX)


def balanced_accuracy_values_by_set(fitnesses_df: DataFrame) -> dict[str, list[float]]:
    """
    Obtiene los valores de balanced accuracy para:

        - train
        - inner cv
        - test
    """
    result = {}

    #Busca las columnas de balanced accuracy disponibles
    inner_cv_column = inner_cv_balanced_accuracy_column(df=fitnesses_df)
    train_column = train_balanced_accuracy_column(df=fitnesses_df)
    test_column = test_balanced_accuracy_column(df=fitnesses_df)

    #Guarda los valores de train si existe la columna
    if train_column is not None:
        result["train"] = fitnesses_df[train_column].tolist()

    #Guarda los valores de inner CV si existe la columna
    if inner_cv_column is not None:
        result["inner cv"] = fitnesses_df[inner_cv_column].tolist()

    #Guarda los valores de test si existe la columna
    if test_column is not None:
        result["test"] = fitnesses_df[test_column].tolist()

    return result


def plot_hyperparameter_vs_balanced_accuracy(hyperparameter_values, balanced_accuracies_by_set: dict[str, list[float]], save_file: str, hyperparameter_name: str):
    """
    Crea una gráfica de dispersión.

    Eje X:
        Valores de un hiperparámetro.

    Eje Y:
        Balanced accuracy.

    Clases:
        - train
        - inner cv
        - test

    El tipo del hiperparámetro se detecta automáticamente.
    """
    #No tiene sentido crear una gráfica sin valores del hiperparámetro
    if len(hyperparameter_values) == 0:
        return

    x = []
    y = []
    class_labels = []

    #Recorre los diferentes conjuntos de evaluación
    for (set_name, balanced_accuracies) in balanced_accuracies_by_set.items():
        #Ignora los conjuntos que no tienen valores
        if len(balanced_accuracies) == 0:
            continue

        #Cada valor del hiperparámetro debe tener su balanced accuracy correspondiente
        if len(hyperparameter_values) != len(balanced_accuracies):
            raise ValueError(
                "Different number of hyperparameter values and balanced accuracy values for "
                f"hyperparameter '{hyperparameter_name}'. Hyperparameters: {len(hyperparameter_values)}. "
                f"Balanced accuracies ({set_name}): {len(balanced_accuracies)}."
            )

        #Añade los valores del hiperparámetro para este conjunto
        x.append(hyperparameter_values)

        #Añade los valores de balanced accuracy
        y.append(balanced_accuracies)

        #Guarda el nombre del conjunto como etiqueta de la clase
        class_labels.append(set_name)

    #Si no hay ningún conjunto válido, no crea la gráfica
    if len(x) == 0:
        return

    #Crea la gráfica utilizando la función común
    save_hyperparameter_multiclass_scatter(x=x, y=y, save_file=save_file, x_label=hyperparameter_name, y_label="balanced accuracy", class_labels=class_labels)


def fold_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_file: str, fitnesses_file: str, plot_dir: str, fold_number: int):
    """
    Crea una gráfica para cada hiperparámetro de un fold.
    """
    #Lee los hiperparámetros y fitness del fold
    hyperparameters_df = read_hyperparameters(file_path=hyperparameters_file)
    fitnesses_df = read_fitnesses(file_path=fitnesses_file)

    #Obtiene los valores de balanced accuracy de cada conjunto
    balanced_accuracies_by_set = balanced_accuracy_values_by_set(fitnesses_df=fitnesses_df)

    #Crea una gráfica para cada hiperparámetro
    for hyperparameter_name in hyperparameters_df.columns:
        hyperparameter_values = hyperparameters_df[hyperparameter_name].tolist()

        #Construye el nombre del archivo de salida
        save_file = os.path.join(plot_dir, hyperparameter_name + "_balanced_accuracy_fold_" + str(fold_number) + ".png")

        #Crea la gráfica del hiperparámetro frente a balanced accuracy
        plot_hyperparameter_vs_balanced_accuracy(hyperparameter_values=hyperparameter_values, balanced_accuracies_by_set=balanced_accuracies_by_set, save_file=save_file, hyperparameter_name=hyperparameter_name)


def union_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_dfs: list[DataFrame], fitnesses_dfs: list[DataFrame], plot_dir: str):
    """
    Crea una gráfica para cada hiperparámetro utilizando la unión de las soluciones de todos los folds.

    La solución final no se incluye.
    """
    #Si no existen dataframes, no hay nada que representar
    if len(hyperparameters_dfs) == 0:
        return

    #Debe existir un dataframe de fitness por cada dataframe de hiperparámetros
    if len(hyperparameters_dfs) != len(fitnesses_dfs):
        raise ValueError("Different number of hyperparameter and fitnesses dataframes.")

    first_hyperparameters_df = hyperparameters_dfs[0]

    #Recorre todos los hiperparámetros
    for hyperparameter_name in first_hyperparameters_df.columns:
        union_hyperparameter_values = []

        union_balanced_accuracies_by_set = {
            "train": [],
            "inner cv": [],
            "test": []
        }

        #Recorre los resultados de todos los folds
        for (hyperparameters_df, fitnesses_df) in zip(hyperparameters_dfs, fitnesses_dfs):
            #Todos los folds deben contener el mismo hiperparámetro
            if hyperparameter_name not in hyperparameters_df.columns:
                raise ValueError("Hyperparameter '" + hyperparameter_name + "' is not present in every fold.")

            #Obtiene los valores del hiperparámetro del fold actual
            hyperparameter_values = hyperparameters_df[hyperparameter_name].tolist()

            #Obtiene los valores de balanced accuracy del fold
            balanced_accuracies_by_set = balanced_accuracy_values_by_set(fitnesses_df=fitnesses_df)

            #Añade los valores del hiperparámetro a la unión
            union_hyperparameter_values.extend(hyperparameter_values)

            #Añade los valores de balanced accuracy de cada conjunto
            for (set_name, balanced_accuracies) in balanced_accuracies_by_set.items():
                #Inicializa el conjunto si aparece por primera vez
                if set_name not in union_balanced_accuracies_by_set:
                    union_balanced_accuracies_by_set[set_name] = []

                union_balanced_accuracies_by_set[set_name].extend(balanced_accuracies)

        #Elimina los conjuntos que no contienen ningún valor
        union_balanced_accuracies_by_set = {
            set_name: values
            for (set_name, values) in union_balanced_accuracies_by_set.items()
            if len(values) > 0
        }

        #Construye el nombre del archivo de salida
        save_file = os.path.join(plot_dir, hyperparameter_name + "_balanced_accuracy.png")

        #Crea la gráfica utilizando la unión de todos los folds
        plot_hyperparameter_vs_balanced_accuracy(hyperparameter_values=union_hyperparameter_values, balanced_accuracies_by_set=union_balanced_accuracies_by_set, save_file=save_file, hyperparameter_name=hyperparameter_name)


def final_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_file: str, fitnesses_file: str, plot_dir: str):
    """
    Crea una gráfica para cada hiperparámetro utilizando las soluciones finales.

    La evaluación final normalmente contiene:

        - inner cv
        - train

    pero no contiene valores de test.
    """
    #Lee los hiperparámetros y fitness finales
    hyperparameters_df = read_hyperparameters(file_path=hyperparameters_file)
    fitnesses_df = read_fitnesses(file_path=fitnesses_file)

    #Obtiene los valores de balanced accuracy disponibles
    balanced_accuracies_by_set = balanced_accuracy_values_by_set(fitnesses_df=fitnesses_df)

    #Crea una gráfica para cada hiperparámetro
    for hyperparameter_name in hyperparameters_df.columns:
        hyperparameter_values = hyperparameters_df[hyperparameter_name].tolist()

        #Construye el nombre del archivo de salida
        save_file = os.path.join(plot_dir, hyperparameter_name + "_balanced_accuracy_final.png")

        #Crea la gráfica del hiperparámetro frente a balanced accuracy
        plot_hyperparameter_vs_balanced_accuracy(hyperparameter_values=hyperparameter_values, balanced_accuracies_by_set=balanced_accuracies_by_set, save_file=save_file, hyperparameter_name=hyperparameter_name)


def hof_hyperparameter_accuracy_plots_for_directory(hof_dir: str):
    """
    Crea gráficas de hiperparámetros frente a balanced accuracy para un HOF.

    Archivos de entrada esperados:

        solution_hyperparameters_fold_0.csv
        solution_fitnesses_fold_0.csv

        solution_hyperparameters_fold_1.csv
        solution_fitnesses_fold_1.csv

        ...

        solution_hyperparameters_final.csv
        solution_fitnesses_final.csv

    Salida:

        hof_dir/hyperparameters/
    """
    #Si el directorio no existe, no hay nada que procesar
    if not os.path.isdir(hof_dir):
        return

    #Crea el directorio donde se guardarán las gráficas
    plot_dir = create_plot_directory(directory=os.path.join(hof_dir, HYPERPARAMETERS_DIR))

    #Obtiene los archivos de hiperparámetros y fitness de todos los folds
    hyperparameters_files_by_fold = hyperparameters_fold_files(hof_dir=hof_dir)
    fitnesses_files_by_fold = fitnesses_fold_files(hof_dir=hof_dir)

    #Busca los folds que tienen ambos archivos
    common_folds = sorted(set(hyperparameters_files_by_fold.keys()) & set(fitnesses_files_by_fold.keys()))

    hyperparameters_dfs = []
    fitnesses_dfs = []

    #Lee los resultados de todos los folds comunes
    for fold_number in common_folds:
        hyperparameters_file = hyperparameters_files_by_fold[fold_number]
        fitnesses_file = fitnesses_files_by_fold[fold_number]

        #Descomentar si se quieren crear las gráficas de cada hiperparámetro por fold
        #fold_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_file=hyperparameters_file, fitnesses_file=fitnesses_file, plot_dir=plot_dir, fold_number=fold_number)

        hyperparameters_dfs.append(read_hyperparameters(file_path=hyperparameters_file))
        fitnesses_dfs.append(read_fitnesses(file_path=fitnesses_file))

    #Crea las gráficas utilizando la unión de todos los folds
    union_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_dfs=hyperparameters_dfs, fitnesses_dfs=fitnesses_dfs, plot_dir=plot_dir)

    #Busca los archivos de resultados finales
    final_hyperparameters_file = hyperparameters_final_file(hof_dir=hof_dir)
    final_fitnesses_file = fitnesses_final_file(hof_dir=hof_dir)

    #Si existen ambos archivos finales, crea las gráficas finales
    if final_hyperparameters_file is not None and final_fitnesses_file is not None:
        final_hyperparameters_vs_balanced_accuracy_plots(hyperparameters_file=final_hyperparameters_file, fitnesses_file=final_fitnesses_file, plot_dir=plot_dir)


def hof_hyperparameter_accuracy_plots_every_hof(main_hofs_dir: str):
    """
    Crea gráficas de hiperparámetros frente a balanced accuracy para todos los HOF.

    Ejemplo:

        hofs/
        ├── pareto/
        ├── sum50/
        └── ...
    """
    #Obtiene todos los subdirectorios que representan un HOF
    subfolders = hof_subdirectories(main_hofs_dir=main_hofs_dir)

    #Procesa cada HOF individualmente
    for hof_dir in subfolders:
        hof_hyperparameter_accuracy_plots_for_directory(hof_dir=hof_dir)