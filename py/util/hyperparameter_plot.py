import math
import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
from pandas import DataFrame


LOG_SCALE_MIN_RATIO = 100

SOLUTION_HYPERPARAMETERS_PREFIX = "solution_hyperparameters"

FOLD_FILE_REGEX = re.compile(r"_fold_(\d+)\.csv$")


def is_missing_value(value) -> bool:
    """
    Devuelve True cuando el valor representa un valor ausente. (None, np.nan, pd.NA)
    """
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def numeric_values_or_none(values) -> Optional[list[float]]:
    """
    Convierte los valores en valores numéricos.

    Los valores ausentes se ignoran al determinar
    si todos los valores son numéricos.

    Devuelve None cuando al menos un valor no ausente
    no puede convertirse en un número finito.
    """
    numeric_values = []

    for value in values:
        if is_missing_value(value=value):
            continue

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(numeric_value):
            return None

        #Añade valores numericos a la lista
        numeric_values.append(numeric_value)

    return numeric_values


def hyperparameter_is_numeric(values) -> bool:
    """
    Devuelve True cuando todos los valores son numericos.
    """
    numeric_values = numeric_values_or_none(values=values)

    return (
        numeric_values is not None
        and len(numeric_values) > 0
    )


def hyperparameter_is_integer(values) -> bool:
    """
    Devuelve True cuando todos los valores son enteros.
    """
    numeric_values = numeric_values_or_none(values=values)

    if numeric_values is None or len(numeric_values) == 0:
        return False

    #Recorre la lista comprobando si es entero cada valor
    return all(
        value.is_integer()
        for value in numeric_values
    )


def hyperparameter_should_use_log_scale(values) -> bool:
    """
    Determina si el hiperparametro debe usar escala logaritmica.

    Reglas:
        - categórico -> no logarítmica
        - entero -> escala lineal
        - cero o valores negativos -> escala lineal
        - valores positivos de tipo float con un rango
          de al menos dos órdenes de magnitud
          -> escala logarítmica
    """
    numeric_values = numeric_values_or_none(values=values)

    #No es numérico o no tiene suficientes valores
    if numeric_values is None or len(numeric_values) < 2:
        return False

    #Los valores enteros siempre utilizan escala lineal
    if hyperparameter_is_integer(values=values):
        return False

    #Si solo existe un valor distinto, no hay rango
    unique_values = sorted(set(numeric_values))

    if len(unique_values) < 2:
        return False

    minimum_value = min(unique_values)
    maximum_value = max(unique_values)

    #La escala logarítmica no puede utilizar cero o negativos
    if minimum_value <= 0:
        return False

    ratio = maximum_value / minimum_value

    #Comprueba si el rango es suficientemente amplio
    return ratio >= LOG_SCALE_MIN_RATIO


def categorical_value(value) -> str:
    """
    Convierte el valor categorico a una etiqueta.

    Un valor perdido será representado como:
        None
    """
    if is_missing_value(value=value):
        return "None"

    return str(value)


def categorical_information(values) -> tuple[list[str], dict[str, int]]:
    """
    Crea las etiquetas de las categorias y su posición.
    """
    labels = []

    for value in values:
        label = categorical_value(value=value)

        #Añade las categorias no repetidas
        if label not in labels:
            labels.append(label)

    positions = {
        label: position
        for position, label in enumerate(labels)
    }

    #Coloca la posición numerica de la categoria para representarla
    return (labels,positions)


def fold_number_from_file_name(file_name: str) -> Optional[int]:
    """
    Obtiene el numero de fold a partir del nombre
    de un archivo.

    Ejemplos:

        solution_hyperparameters_fold_0.csv
            -> 0

        solution_fitnesses_fold_12.csv
            -> 12

        solution_hyperparameters_final.csv
            -> None
    """
    #Busca el numero del fold dentro del nombre del archivo
    match = FOLD_FILE_REGEX.search(file_name)

    #Si el archivo no contiene un numero de fold, devuelve None
    if match is None:
        return None

    #Extrae y devuelve el numero del fold
    return int(match.group(1))


def is_csv_file_with_prefix(file_name: str, prefix: str) -> bool:
    """
    Comprueba si un archivo:

        - Comienza con el prefijo indicado.
        - Tiene extension CSV.
    """
    return (
        file_name.startswith(prefix)
        and file_name.endswith(".csv")
    )


def fold_files_by_prefix(directory: str, prefix: str) -> dict[int, str]:
    """
    Obtiene los archivos CSV de todos los folds
    indexados por su numero de fold.

    Solo se incluyen los archivos cuyo nombre:

        - Comienza con el prefijo indicado.
        - Tiene extension CSV.
        - Contiene un numero de fold.
    """
    result = {}

    #Si el directorio no existe, no hay archivos que procesar
    if not os.path.isdir(directory):
        return result

    #Recorre todos los archivos del directorio
    for file_name in os.listdir(directory):
        #Ignora los archivos que no tienen el prefijo esperado
        if not is_csv_file_with_prefix(file_name=file_name, prefix=prefix):
            continue

        #Obtiene el numero del fold a partir del nombre
        fold_number = fold_number_from_file_name(file_name=file_name)

        #Solo guarda los archivos asociados a un fold
        if fold_number is not None:
            result[fold_number] = os.path.join(directory,file_name)

    return result


def final_file_by_prefix(directory: str, prefix: str) -> Optional[str]:
    """
    Obtiene el archivo final correspondiente
    al prefijo indicado.

    El archivo esperado es: <prefix>_final.csv
    """
    file_path = os.path.join(directory,prefix + "_final.csv")

    #Comprueba si el archivo final existe
    if os.path.isfile(file_path):
        return file_path

    return None


def hyperparameters_fold_files(hof_dir: str) -> dict[int, str]:
    """
    Obtiene los archivos de hiperparametros de
    cada fold indexados por su numero de fold.
    """
    return fold_files_by_prefix(directory=hof_dir,prefix=SOLUTION_HYPERPARAMETERS_PREFIX)


def hyperparameters_final_file(hof_dir: str) -> Optional[str]:
    """
    Obtiene el archivo final de hiperparametros
    si existe.
    """
    return final_file_by_prefix(directory=hof_dir,prefix=SOLUTION_HYPERPARAMETERS_PREFIX)


def read_hyperparameters(file_path: str) -> DataFrame:
    """
    Lee un archivo CSV de hiperparametros y
    devuelve su contenido como un DataFrame.
    """
    return pd.read_csv(file_path)


def hyperparameter_values_are_constant(hyperparameter_values) -> bool:
    """
    Devuelve True cuando todos los valores no
    ausentes de un hiperparametro son iguales.

    Un hiperparametro constante no proporciona
    informacion util en una grafica de relacion
    o distribucion.
    """
    #Convierte los valores en una Serie de pandas
    series = pd.Series(hyperparameter_values)

    #Elimina los valores ausentes y los valores repetidos
    unique_values = (series.dropna().drop_duplicates())

    #Un unico valor diferente significa que es constante
    return len(unique_values) <= 1


def create_plot_directory(directory: str) -> str:
    """
    Crea un directorio de salida para las
    graficas si no existe.

    Devuelve la ruta del directorio creado.

    Esto sucede ya que es un hiperparametro no mutable
    """
    Path(directory).mkdir(parents=True,exist_ok=True)
    return directory


def hof_subdirectories(main_hofs_dir: str) -> list[str]:
    """
    Obtiene todos los subdirectorios de un
    directorio principal de Hall Of Fame.

    Si el directorio principal no existe,
    devuelve una lista vacia.
    """
    #Si el directorio principal no existe, no hay HOFs
    if not os.path.isdir(main_hofs_dir):
        return []

    #Obtiene todos los subdirectorios
    return [
        folder.path
        for folder in os.scandir(main_hofs_dir)
        if folder.is_dir()
    ]