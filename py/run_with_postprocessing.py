import sys

from consts import DEFAULT_RECURSION_LIMIT
from postprocessing.postprocessing import run_postprocessing_archive
from util.printer.printer import Printer


class ConsolePrinter(Printer):
    def print(self, text: str):
        print(text)


def run_one_postprocessing(optimizer_dir: str):
    printer = ConsolePrinter()

    printer.print(f"Starting postprocessing: {optimizer_dir}")

    run_postprocessing_archive(
        optimizer_dir=optimizer_dir,
        printer=printer
    )

    printer.print(f"Finished postprocessing: {optimizer_dir}")


def main():
    sys.setrecursionlimit(DEFAULT_RECURSION_LIMIT)

    optimizer_dirs = sys.argv[1:]

    if not optimizer_dirs:
        print("Usage:")
        print(
            "python ../py/run_with_postprocessing.py "
            "<optimizer_dir_1> <optimizer_dir_2> ..."
        )
        sys.exit(1)

    for optimizer_dir in optimizer_dirs:
        run_one_postprocessing(optimizer_dir)

    print("All postprocessing finished.")


if __name__ == "__main__":
    main()