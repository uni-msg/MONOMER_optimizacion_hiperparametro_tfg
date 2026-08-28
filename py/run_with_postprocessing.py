import sys

from consts import DEFAULT_RECURSION_LIMIT
from cross_validation.multi_objective.multi_objective_cross_validation import create_optimizer_save_path
from postprocessing.postprocessing import run_postprocessing_archive
from setup.evaluation_setup import EvaluationSetup
from setup.setup_reader import read_all_setups_in_argv
from setup.setup_to_mo_optimizer import setup_to_mo_optimizer
from setup.setup_utils import save_path_from_components, setup_to_folds
from util.printer.printer import Printer


class ConsolePrinter(Printer):

    def print(self, text: str):
        print(text)


def run_one_postprocessing(setup: EvaluationSetup, printer: Printer):
    """
    Ejecuta únicamente el postprocesamiento de una
    optimización ya realizada.

    Reconstruye la ruta donde se guardaron los
    resultados a partir del setup y ejecuta el
    postprocesamiento sobre los archivos existentes.
    """

    # Reconstruye el optimizador y los datos para obtener exactamente la misma configuración
    mo_optimizer, input_data, objectives = setup_to_mo_optimizer(setup=setup, printer=printer)

    # Reconstruye los folds para obtener el mismo número de folds utilizado en la ruta original
    outer_folds = setup_to_folds(setup=setup, input_data=input_data, printer=printer)
    outer_n_folds = outer_folds.n_folds()

    printer.print_variable("Number of outer folds", outer_n_folds)

    # Reconstruye la ruta base original
    save_path = save_path_from_components(
        input_data_nick=input_data.nick(),
        views_to_use=input_data.view_names(),
        objectives=objectives,
        uses_inner_models=mo_optimizer.uses_inner_models(),
        outer_n_folds=outer_n_folds
    )

    # Reconstruye la ruta exacta del optimizador
    optimizer_save_path = create_optimizer_save_path(save_path=save_path, optimizer_nick=mo_optimizer.nick())

    printer.print_variable("Destination folder", optimizer_save_path)

    # Ejecuta únicamente el postprocesamiento sobre los archivos ya existentes
    run_postprocessing_archive(optimizer_dir=optimizer_save_path, printer=printer)


if __name__ == '__main__':

    # Configura el límite de recursión igual que la ejecución normal
    sys.setrecursionlimit(DEFAULT_RECURSION_LIMIT)

    # Crea un printer que únicamente muestra la información por consola
    printer = ConsolePrinter()

    # Lee todos los setups proporcionados como argumentos
    setups = read_all_setups_in_argv(printer=printer)

    # Ejecuta únicamente el postprocesamiento de cada setup
    for setup in setups:
        run_one_postprocessing(setup=setup, printer=printer)