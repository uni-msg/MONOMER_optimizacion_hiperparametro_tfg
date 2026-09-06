import multiprocessing
import sys
import socket
import datetime
import time

from consts import DEFAULT_RECURSION_LIMIT, MAX_WORKERS
from run_one_setup import run_one_setup
from setup.setup_reader import read_all_setups_in_argv
from util.concurrent.exclusive_number import ExclusiveNumber
from util.printer.printer import LogAndOutPrinter
from util.utils import pretty_duration


def run_setup(setup, config_file, n_workers):
    """
    Ejecuta un setup de forma independiente.
    Cada setup tendrá su propio proceso y sus propios workers.
    """
    with ExclusiveNumber() as exclusive_number:

        log_file_name = "temp/log" + str(exclusive_number) + ".txt"

        print(
            "Starting setup "
            + str(config_file)
            + " with "
            + str(n_workers)
            + " workers"
        )

        printer = LogAndOutPrinter(log_file=log_file_name)

        printer.print_variable("Date", datetime.date.today())
        printer.print_variable("Machine", socket.gethostname())
        printer.print_variable("Workers", n_workers)
        printer.print_variable("Setup", config_file)

        sys.setrecursionlimit(DEFAULT_RECURSION_LIMIT)
        printer.print_variable(
            "Recursion limit",
            sys.getrecursionlimit()
        )

        start_time = time.time()

        run_one_setup(
            setup=setup,
            printer=printer,
            n_workers=n_workers,
            config_file=config_file
        )

        printer.print("Setup finished")
        printer.print_variable(
            "Execution time",
            pretty_duration(time.time() - start_time)
        )


if __name__ == '__main__':

    # ---------------------------------------------------------
    # PROCESO PRINCIPAL
    # ---------------------------------------------------------

    cpu_count = multiprocessing.cpu_count()

    print("CPUs detected in the system: " + str(cpu_count))

    # Leer todos los setups antes de crear los procesos.
    setups = read_all_setups_in_argv(
        printer=LogAndOutPrinter(log_file="temp/main_setup_reader.txt")
    )

    number_of_setups = len(setups)

    if number_of_setups == 0:
        print("No setups provided.")
        sys.exit(1)

    # ---------------------------------------------------------
    # CPUs / WORKERS POR SETUP
    # ---------------------------------------------------------

    n_workers = min(
        cpu_count // number_of_setups,
        MAX_WORKERS
    )

    if n_workers < 1:
        print("Not enough CPUs to run all setups in parallel.")
        sys.exit(1)

    print(
        "Running "
        + str(number_of_setups)
        + " setups in parallel with "
        + str(n_workers)
        + " workers each."
    )

    print(
        "Total workers: "
        + str(n_workers * number_of_setups)
    )

    # ---------------------------------------------------------
    # CREAR UN PROCESO POR SETUP
    # ---------------------------------------------------------

    processes = []

    start_time = time.time()

    for i in range(number_of_setups):

        process = multiprocessing.Process(
            target=run_setup,
            args=(
                setups[i],
                sys.argv[i + 1],
                n_workers
            )
        )

        process.start()
        processes.append(process)

        print(
            "Started setup "
            + str(i + 1)
            + "/"
            + str(number_of_setups)
            + ": "
            + sys.argv[i + 1]
        )

    # ---------------------------------------------------------
    # ESPERAR A QUE TERMINEN TODOS
    # ---------------------------------------------------------

    for process in processes:
        process.join()

    # ---------------------------------------------------------
    # RESULTADO
    # ---------------------------------------------------------

    print("All setups finished.")

    for i, process in enumerate(processes):
        print(
            "Setup "
            + str(i + 1)
            + " exit code: "
            + str(process.exitcode)
        )

    print(
        "Total execution time: "
        + pretty_duration(time.time() - start_time)
    )