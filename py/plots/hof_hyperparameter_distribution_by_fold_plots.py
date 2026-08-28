import os

from pandas import DataFrame

from util.hyperparameter_fold_distribution_plot_results import (
    save_hyperparameter_distribution_by_fold
)
from util.hyperparameter_plot import (
    create_plot_directory,
    hof_subdirectories,
    hyperparameter_values_are_constant,
    hyperparameters_fold_files,
    read_hyperparameters
)


HYPERPARAMETERS_DIR = "hyperparameters"


def union_values_from_folds(hyperparameters_dfs_by_fold: dict[int, DataFrame], hyperparameter_name: str):
    """
    Obtiene todos los valores de un
    hiperparametro a partir de todos los folds.
    """
    result = []

    #Recorre los DataFrames de hiperparametros de todos los folds
    for hyperparameters_df in hyperparameters_dfs_by_fold.values():

        #Comprueba que el hiperparametro exista en todos los folds
        if hyperparameter_name not in hyperparameters_df.columns:
            raise ValueError(
                "Hyperparameter '"
                + hyperparameter_name
                + "' is not present "
                "in every fold."
            )

        #Añade los valores del hiperparametro de este fold
        result.extend(
            hyperparameters_df[hyperparameter_name].tolist()
        )

    return result


def hyperparameter_distribution_by_fold_plots_for_directory(hof_dir: str):
    """
    Crea una grafica de distribucion por cada
    hiperparametro no constante.

    Cada grafica muestra como se distribuyen los
    valores del hiperparametro entre los folds.

    Las soluciones finales no se incluyen porque
    el objetivo es comparar las distribuciones
    obtenidas durante los diferentes folds.
    """
    #Construye y crea el directorio donde se guardaran las graficas
    plot_dir = create_plot_directory(directory=os.path.join(hof_dir, HYPERPARAMETERS_DIR))

    #Obtiene los archivos de hiperparametros disponibles para cada fold
    hyperparameters_files_by_fold = hyperparameters_fold_files(hof_dir=hof_dir)

    #Si no existen archivos de folds, no se pueden crear distribuciones
    if len(hyperparameters_files_by_fold) == 0:
        return

    #Lee los hiperparametros y los almacena indexados por numero de fold
    hyperparameters_dfs_by_fold = {
        fold_number: read_hyperparameters(file_path=file_path)
        for (fold_number, file_path) in hyperparameters_files_by_fold.items()
    }

    #Obtiene el primer fold para usar sus columnas como referencia
    first_fold_number = min(hyperparameters_dfs_by_fold.keys())

    first_hyperparameters_df = hyperparameters_dfs_by_fold[first_fold_number]

    #Recorre todos los hiperparametros disponibles
    for hyperparameter_name in first_hyperparameters_df.columns:

        #Une todos los valores del hiperparametro de todos los folds
        all_hyperparameter_values = union_values_from_folds(
            hyperparameters_dfs_by_fold=hyperparameters_dfs_by_fold,
            hyperparameter_name=hyperparameter_name
        )

        #Ignora los hiperparametros que no cambian entre soluciones
        if hyperparameter_values_are_constant(hyperparameter_values=all_hyperparameter_values):
            continue

        values_by_fold = {}

        #Recorre cada fold para separar sus valores
        for fold_number, hyperparameters_df in hyperparameters_dfs_by_fold.items():

            #Comprueba que el hiperparametro exista en el fold actual
            if hyperparameter_name not in hyperparameters_df.columns:
                raise ValueError(
                    "Hyperparameter '"
                    + hyperparameter_name
                    + "' is not present "
                    "in fold "
                    + str(fold_number)
                    + "."
                )

            #Guarda los valores del hiperparametro asociados a este fold
            values_by_fold[fold_number] = hyperparameters_df[hyperparameter_name].tolist()

        #Construye el nombre del archivo de salida
        save_file = os.path.join(plot_dir, hyperparameter_name + "_distribution_by_fold.png")

        #Genera y guarda la grafica de distribucion del hiperparametro
        save_hyperparameter_distribution_by_fold(
            values_by_fold=values_by_fold,
            save_file=save_file,
            hyperparameter_name=hyperparameter_name
        )


def hof_hyperparameter_distribution_by_fold_plots_every_hof(main_hofs_dir: str):
    """
    Crea las graficas de distribucion de
    hiperparametros por fold para todos los
    directorios Hall Of Fame.
    """
    #Obtiene todos los subdirectorios que contienen HOFs
    for hof_dir in hof_subdirectories(main_hofs_dir=main_hofs_dir):

        #Genera las graficas correspondientes para cada HOF
        hyperparameter_distribution_by_fold_plots_for_directory(hof_dir=hof_dir)