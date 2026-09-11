from typing import Sequence

from saved_solutions.run_fold_measure import RunFoldMeasure
from saved_solutions.saved_solution import SavedSolution
from util.cross_hypervolume.cross_hypervolume import cross_hypervolume, hyperbox_with_ref


class RunCrossHypervolume05(RunFoldMeasure):
    """Cross hypervolume with configurable reference point.
    Default ref (0.5, 0) for backward compatibility."""

    def __init__(self, ref: Sequence[float] = (0.5, 0.0)):
        self._ref = list(ref)

    def compute_fold_measure(self, solutions: Sequence[SavedSolution]) -> float:
        return cross_hypervolume(
            train_hyperboxes=[hyperbox_with_ref(s.train_hyperbox(), self._ref) for s in solutions],
            test_hyperboxes=[hyperbox_with_ref(s.test_hyperbox(), self._ref) for s in solutions])

    def name(self) -> str:
        return "cross hypervolume (1/k)"

    def nick(self) -> str:
        return "cross_hypervol_per_class"
