import math
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from util.hyperparameter_plot import categorical_information, categorical_value, hyperparameter_is_numeric, hyperparameter_should_use_log_scale, is_missing_value


def flatten_values(values_by_class) -> list:
    """
    Une todos los valores de las clases
    en una única lista.
    """
    result = []

    # Añade los valores de cada clase a una misma lista
    for values in values_by_class:
        result.extend(values)

    return result


def hyperparameter_has_multiple_values(values) -> bool:
    """
    Devuelve True cuando un hiperparámetro tiene más de un valor diferente.

    Los valores ausentes también se consideran valores diferentes, ya que pueden representar una opción válida como None.
    """
    unique_values = set()
    #Convierte todos los valores a etiquetas comparables
    for value in values:
        unique_values.add(categorical_value(value=value))
    return len(unique_values) > 1


def numeric_x_and_y(x_values, y_values) -> tuple[list[float], list[float]]:
    """
    Limpia los valores de X e Y para que solo se utilicen valores numéricos válidos.
    """
    filtered_x = []
    filtered_y = []
    #Procesa cada pareja X-Y simultáneamente
    for (x_value, y_value) in zip(x_values, y_values):
        if is_missing_value(x_value) or is_missing_value(y_value):
            continue

        try:
            numeric_x = float(x_value)
            numeric_y = float(y_value)
        except (TypeError, ValueError):
            continue

        #Descarta valores infinitos o NaN
        if not math.isfinite(numeric_x) or not math.isfinite(numeric_y):
            continue

        filtered_x.append(numeric_x)
        filtered_y.append(numeric_y)
    return (filtered_x, filtered_y)


def categorical_x_and_y(x_values, y_values, category_positions) -> tuple[list[int], list[float]]:
    """
    Convierte los valores categóricos de X en posiciones numéricas.

    Las filas con valores Y inválidos se ignoran.
    Los valores X ausentes se representan como la categoría None.
    """
    filtered_x = []
    filtered_y = []

    for (x_value, y_value) in zip(x_values, y_values):
        if is_missing_value(y_value):
            continue

        try:
            numeric_y = float(y_value)
        except (TypeError, ValueError):
            continue

        if not math.isfinite(numeric_y):
            continue

        #Convierte la categoría X en su posición numérica
        label = categorical_value(value=x_value)

        filtered_x.append(category_positions[label])
        filtered_y.append(numeric_y)

    return (filtered_x, filtered_y)


def validate_values_by_class(x, y, class_labels):
    """
    Comprueba que las dimensiones de los datos de entrada sean correctas.
    """
    #Debe existir una colección X e Y por cada clase
    if len(x) != len(y):
        raise ValueError("Different number of X and Y datasets.")

    #Debe existir una etiqueta por cada clase
    if len(x) != len(class_labels):
        raise ValueError( "Different number of datasets and class labels." )

    #Comprueba que X e Y tengan la misma cantidad de puntos
    for (x_values, y_values, class_label) in zip(x,y,class_labels):
        if len(x_values) != len(y_values):
            raise ValueError("Different number of X and Y values for class "f"'{class_label}'. "f"X: {len(x_values)}. "f"Y: {len(y_values)}.")


def save_hyperparameter_multiclass_scatter(x,y,save_file: str,x_label: str,y_label: str,class_labels):
    """
    Crea y guarda una gráfica de dispersión de un hiperparámetro comparado con diferentes clases.

    El eje X se selecciona automáticamente:
        1. Valores categóricos -> categórico
        2. Valores enteros -> numérico lineal
        3. Valores float -> numérico lineal
        4. Floats positivos con amplio rango -> numérico logarítmico
    """
    #Comprueba que los datos de entrada sean correctos
    validate_values_by_class(  x=x,  y=y, class_labels=class_labels)

    #Une todos los valores X para determinar su tipo
    all_x_values = flatten_values(values_by_class=x)

    #No tiene sentido crear una gráfica sin variación, hiperparametro no mutable
    if not hyperparameter_has_multiple_values(values=all_x_values):
        return


    #Crea la figura y el sistema de ejes
    figure, axis = plt.subplots()
    plotted_class_labels = []

    #Determina si el eje X es numérico o categórico
    numeric = hyperparameter_is_numeric(values=all_x_values)
    if numeric:
        #Dibuja cada clase por separado
        for (x_values, y_values, class_label) in zip( x, y, class_labels ):
            #Limpia y prepara los valores numéricos
            (numeric_x, numeric_y) = numeric_x_and_y( x_values=x_values, y_values=y_values )
            if len(numeric_x) == 0:
                continue

            #Añade los puntos de la clase a la gráfica
            axis.scatter( numeric_x, numeric_y, label=class_label )
            plotted_class_labels.append(class_label)

        #Determina si el eje X debe utilizar escala logarítmica
        use_log_scale = hyperparameter_should_use_log_scale( values=all_x_values )
        if use_log_scale:
            axis.set_xscale("log")

    else:
        #Crea las categorías y sus posiciones en el eje X
        (category_labels, category_positions) = categorical_information( values=all_x_values )

        #Dibuja cada clase utilizando las posiciones categóricas
        for (x_values, y_values, class_label) in zip( x, y, class_labels ):
            (categorical_x, numeric_y) = categorical_x_and_y( x_values=x_values, y_values=y_values, category_positions=category_positions )
            if len(categorical_x) == 0:
                continue

            #Añade los puntos de la clase a la gráfica
            axis.scatter( categorical_x, numeric_y, label=class_label )
            plotted_class_labels.append(class_label)

        #Configura las posiciones y nombres de las categorías
        axis.set_xticks(list(range(len(category_labels))))
        axis.set_xticklabels( category_labels, rotation=45, ha="right" )

    #Añade las etiquetas de los ejes
    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)

    #Añade ajustes a la gráfica
    axis.grid(True)
    if len(plotted_class_labels) > 0:
        axis.legend()
    figure.tight_layout()

    figure.savefig(save_file) #Guarda la gráfica en el archivo indicado
    plt.close(figure)