import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from util.hyperparameter_plot import categorical_information, categorical_value, hyperparameter_is_numeric, hyperparameter_should_use_log_scale, is_missing_value

def numeric_values_by_fold(values_by_fold: dict[int,list]) -> dict[int,list[float]]:
    """
    Limpia y prepara los valores numericos del hiperparametro de cada fold.
    """
    result = {}
    for (fold_number,values) in (values_by_fold.items()):
        numeric_values = []
        for value in values:
            if is_missing_value(value):
                continue

            try:
                numeric_value = float(value)
            except (TypeError,ValueError):
                continue

            if math.isfinite(numeric_value):
                numeric_values.append(numeric_value)

        result[fold_number] = numeric_values
    return result


def categorical_values_by_fold(values_by_fold: dict[int,list],category_positions: dict[str,int]) -> dict[int,list[int]]:
    """
    Limpia y prepara los valores categóricos del hiperparametro de cada fold.
    """
    result = {}
    for (fold_number,values) in (values_by_fold.items()):
        result[fold_number] = [category_positions[categorical_value(value=value)]for value in values]
    return result


def jittered_positions( position: int, number_of_values: int) -> np.ndarray:
    """
    Crea posiciones ligeramente desplazadas en el eje X para que los puntos superpuestos sigan siendo visibles.
    Permite ver las zonas mas cargadas de manera más sencilla.
    """
    if number_of_values == 0:
        return np.array([])
    return (np.full(number_of_values,position,dtype=float)+ np.random.uniform(-0.18,0.18,size=number_of_values))


def save_hyperparameter_distribution_by_fold(values_by_fold: dict[int,list],save_file: str,hyperparameter_name: str):
    """
    Crea graficas de distribucion de valores de un hiperparametro por cada fold.

    Eje X: numero del fold

    Eje y: Valor hiperparametro

    Hiperparametros numericos:
        - int -> eje lineal
        - float -> linear axis
        - amplio rango float -> logarithmic axis

    Hiperparametros categórico: Eje y -> categoría.

    Todos los valores tienen un poco de desplazamiento para que no se superponga los datos
    """
    # Comprueba si hay folds
    if len(values_by_fold) == 0:
        return

    # Ordena los folds y agrupa los valores
    sorted_folds = sorted(values_by_fold.keys())
    all_values = []
    for values in (values_by_fold.values()):
        all_values.extend(values)

    # Creación de figura y posicion de los folds (X)
    figure, axis = plt.subplots()
    fold_positions = {
        fold_number: position
        for (position,fold_number) in enumerate(sorted_folds)
    }

    # Si el los valores son numéricos 
    numeric = (hyperparameter_is_numeric(values=all_values))
    if numeric:
        # Prepara el formato de valores numericos
        numeric_by_fold = (numeric_values_by_fold(values_by_fold=(values_by_fold)))
        for fold_number in sorted_folds:
            values = (numeric_by_fold[fold_number])
            if len(values) == 0:
                continue
            x_positions = (jittered_positions(position=(fold_positions[fold_number]),number_of_values=(len(values))))
            # Coloca los valores en la gráfica de dispersión
            axis.scatter(x_positions,values)

        # Si tiene valores log, el y sera log
        use_log_scale = (hyperparameter_should_use_log_scale(values=all_values))
        if use_log_scale:
            axis.set_yscale("log")
    else:
        # Prepara el formato de valores categóricos
        (category_labels,category_positions) = (categorical_information(values=all_values))
        categorical_by_fold = (categorical_values_by_fold(values_by_fold=(values_by_fold),category_positions=(category_positions)))
        for fold_number in sorted_folds:
            values = (categorical_by_fold[fold_number])
            if len(values) == 0:
                continue
            x_positions = (jittered_positions(position=(fold_positions[fold_number]),number_of_values=(len(values))))
            # Coloca los valores en la gráfica de dispersión
            axis.scatter(x_positions,values)
        # Cambia la etiqueta del eje Y al nombre de la categoría
        axis.set_yticks(list(range(len(category_labels))))
        axis.set_yticklabels(category_labels)

    # Cambia la etiqueta del eje X por fold_(valorX)
    axis.set_xticks(list(fold_positions.values()))
    axis.set_xticklabels([
            "fold "+ str(fold_number)
            for fold_number in sorted_folds
        ])

    # Nombres por la gráfica y ajustes
    axis.set_xlabel("fold")
    axis.set_ylabel(hyperparameter_name)
    axis.set_title(hyperparameter_name+ " distribution by fold")
    axis.grid(True,axis="y")
    figure.tight_layout()
    figure.savefig(save_file)
    plt.close(figure)