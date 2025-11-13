"""
Heuristics Module

In branch-and-bound, a relaxation gives an upper bound on the best objective in a branch.
To tighten pruning, you need feasible (integral) solutions to serve as lower bounds.
Instead of waiting for an integral node, you can derive feasible solutions from the relaxation
(e.g., rounding, greedy inclusion) to improve search efficiency.

You can implement heuristics by subclassing `Heuristics` and overriding `search(instance, node)`.
`search` should yield zero or more feasible `RelaxedSolution` objects.
"""

import math
from abc import ABC, abstractmethod
from typing import Tuple

from .instance import Instance
from .relaxed_solution import RelaxedSolution


class HeuristicSolution(RelaxedSolution):
    """
    A feasible heuristic solution.
    Inherits from `RelaxedSolution` for compatibility with the rest of the codebase.
    """

    def copy(self) -> "HeuristicSolution":
        """
        Return a deep copy of this heuristic solution.
        """
        return HeuristicSolution(
            self.instance,
            list(self.selection),
            self.upper_bound,
        )


class Heuristics(ABC):
    """
    Abstract base for heuristic generators.

    Implement `search` to produce feasible solutions from a node's relaxed solution.
    """

    @abstractmethod
    def search(
        self, instance: Instance, relaxed: RelaxedSolution
    ) -> Tuple[HeuristicSolution, ...]:
        """
        Return a tuple of feasible `HeuristicSolution` objects for pruning.
        """
        ...


class MyHeuristic(Heuristics):
    """
    Your heuristic implementation.

    The simplest heuristic returns the node's relaxed solution
    if it is already feasible (integral and within capacity).
    """

    def search(
        self, instance: Instance, relaxed: RelaxedSolution
    ) -> Tuple[HeuristicSolution, ...]:
        relaxed = relaxed.copy()
        selection = relaxed.selection.copy()
        items = relaxed.instance.items
        for i, val in enumerate(selection):
            if 0.0 < val < 1.0:
                selection[i] = 0.0
                break

        not_used = [i for i, val in enumerate(selection) if val == 0.0]
        not_used.sort(key=lambda i: items[i].weight/items[i].value)
        used_weight = 0
        upper = 0
        for i, val in enumerate(selection):
            if val == 1.0:
                used_weight += items[i].weight
                upper += items[i].value

        remaining = instance.capacity - used_weight
        for i in not_used:
            if items[i].weight <= remaining:
                selection[i] = 1.0
                upper += items[i].value
                remaining -= items[i].weight

        return (HeuristicSolution(instance, selection, upper),)

