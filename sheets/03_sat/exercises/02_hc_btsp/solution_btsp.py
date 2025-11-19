import math
from enum import Enum
from os import remove

import networkx as nx
from networkx.classes import edges

from _timer import Timer
from solution_hamiltonian import HamiltonianCycleModel


class SearchStrategy(Enum):
    """
    Different search strategies for the solver.
    """

    SEQUENTIAL_UP = 1  # Try smallest possible k first.
    SEQUENTIAL_DOWN = 2  # Try any improvement.
    BINARY_SEARCH = 3  # Try a binary search for the optimal k.

    def __str__(self):
        return self.name.title()

    @staticmethod
    def from_str(s: str):
        return SearchStrategy[s.upper()]


class BottleneckTSPSolver:
    def __init__(self, graph: nx.Graph) -> None:
        """
        Creates a solver for the Bottleneck Traveling Salesman Problem on the given networkx graph.
        You can assume that the input graph is complete, so all nodes are neighbors.
        The distance between two neighboring nodes is a numeric value (int / float), saved as
        an edge data parameter called "weight".
        There are multiple ways to access this data, and networkx also implements
        several algorithms that automatically make use of this value.
        Check the networkx documentation for more information!
        """
        self.graph = graph
        # TODO: Implement me!
        self.sorted_lengths = sorted(self.graph.edges, key=lambda e: self.graph.edges[e]["weight"])



    def lower_bound(self) -> float:
        # TODO: Implement me!
        return 0.0



    def optimize_bottleneck(
        self,
        time_limit: float = math.inf,
        search_strategy: SearchStrategy = SearchStrategy.BINARY_SEARCH,
    ) -> list[tuple[int, int]] | None:
        """
        Find the optimal bottleneck tsp tour.
        """
        self.timer = Timer(time_limit)
        best_sol = None
        lower = 0
        upper = len(self.sorted_lengths) - 1
        while True:
            index = (upper + lower) // 2
            graph_copy = self.graph.copy()
            graph_copy.remove_edges_from(self.sorted_lengths[index + 1:])
            model = HamiltonianCycleModel(graph_copy)
            result = model.solve()
            if result is not None:
                best_sol = result
                upper = index - 1
                self.graph = graph_copy
            else:
                lower = index + 1
            if upper <= lower:
                return best_sol
