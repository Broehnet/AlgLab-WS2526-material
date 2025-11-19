import bisect
import logging
import math
from typing import Iterable

import networkx as nx
from networkx.classes import neighbors
from pydantic.v1 import NoneIsAllowedError
from pysat.solvers import Solver as SATSolver

logging.basicConfig(level=logging.INFO)

# Define the node ID type. It is an integer but this helps to make the code more readable.
NodeId = int


class Distances:
    """
    This class provides a convenient interface to query distances between nodes in a graph.
    All distances are precomputed and stored in a dictionary, making lookups efficient.
    """

    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph
        self._distances = dict(nx.all_pairs_dijkstra_path_length(self.graph))

    def all_vertices(self) -> Iterable[NodeId]:
        """Returns an iterable of all node IDs in the graph."""
        return self._distances.keys()

    def dist(self, u: NodeId, v: NodeId) -> float:
        """Returns the distance between nodes `u` and `v`."""
        return self._distances[u].get(v, math.inf)

    def max_dist(self, centers: Iterable[NodeId]) -> float:
        """Returns the maximum distance from any node to the closest center."""
        return max(min(self.dist(c, u) for c in centers) for u in self.all_vertices())

    def vertices_in_range(self, u: NodeId, limit: float) -> Iterable[NodeId]:
        """Returns an iterable of nodes within `limit` distance from node `u`."""
        return (v for v, d in self._distances[u].items() if d <= limit)

    def sorted_distances(self) -> list[float]:
        """Returns a sorted list of all pairwise distances in the graph."""
        return sorted(
            dist
            for dist_dict in self._distances.values()
            for dist in dist_dict.values()
        )


class KCenterDecisionVariant:
    def __init__(self, distances: Distances, k: int) -> None:
        self.distances = distances
        self.node_to_var = {node: i+1 for i, node in enumerate(self.distances.all_vertices())}
        self.var_to_node = {var: node for node, var in self.node_to_var.items()}
        # TODO: Implement me!
        # Solution model
        self._solution: list[NodeId] | None = None
        self.k = k
        self.solver = SATSolver("Minicard")
        self.max_dist = math.inf
        self.solver.add_atmost([self.node_to_var[node] for node in self.distances.all_vertices()], self.k)
        self.unsat = False

    def limit_distance(self, limit: float) -> None:
        """Adds constraints to the SAT solver to ensure coverage within the given distance."""
        logging.info("Limiting to distance: %f", limit)
        # TODO: Implement me!
        nodes = list(self.distances.all_vertices())
        for u in nodes:
            nodes_in_limit = self.distances.vertices_in_range(u, limit)
            if not nodes_in_limit:
                self.unsat = True
                return
            self.solver.add_clause([self.node_to_var[node] for node in nodes_in_limit])


    def solve(self) -> list[NodeId] | None:
        """Solves the SAT problem and returns the list of selected nodes, if feasible."""
        if self.unsat:
            return None
        if not self.solver.solve():
            return None
        true_vars = {var for var in self.solver.get_model() if var > 0}
        self._solution = []
        for var in true_vars:
            self._solution.append(self.var_to_node[var])
        return self._solution

    def get_solution(self) -> list[NodeId]:
        """Returns the solution if available; raises an error otherwise."""
        if self._solution is None:
            msg = "No solution available. Ensure `solve` is called first."
            raise ValueError(msg)
        return self._solution




class KCentersSolver:
    def __init__(self, graph: nx.Graph) -> None:
        """
        Creates a solver for the k-centers problem on the given networkx graph.
        The graph may not be complete, and edge weights are used to represent distances.
        """
        self.graph = graph
        self.distances = Distances(self.graph)
        # TODO: Implement me!

    def solve_heur(self, k: int) -> list[NodeId]:
        """
        Calculate a heuristic solution to the k-centers problem.
        Returns the k selected centers as a list of node IDs.
        """
        # TODO: Implement me!
        if k > len(list(self.distances.all_vertices())):
            raise ValueError("k > |nodes|")
        centers = [next(iter(self.distances.all_vertices()))]
        for _ in range(1, k):
            current_center = None
            current_max = 0
            for u in self.distances.all_vertices():
                if u in centers:
                    continue
                min_dist = min(self.distances.dist(u, v) for v in centers)
                if  min_dist > current_max:
                    current_max = min_dist
                    current_center = u
            centers.append(current_center)
        return centers


    def solve(self, k: int) -> list[NodeId]:
        """
        Calculate the optimal solution to the k-centers problem for the given k.
        Returns the selected centers as a list of node IDs.
        """
        # Start with a heuristic solution
        sorted_distances = sorted(set(self.distances.sorted_distances()))
        centers = self.solve_heur(k)
        obj = self.distances.max_dist(centers)
        upper = sorted_distances.index(obj)
        decision_variant = KCenterDecisionVariant(self.distances, k)
        last_index = math.inf
        target = obj / 2
        lower = 0
        for i in range(len(sorted_distances)-1):
            if sorted_distances[i + 1] > target:
                break
            lower = i
        best_sol = None
        while True:
            index = (upper + lower) // 2
            if last_index < index:
                decision_variant = KCenterDecisionVariant(self.distances, k)
            obj = sorted_distances[index]
            decision_variant.limit_distance(obj)
            sol = decision_variant.solve()
            if sol is None:
                lower = index + 1
            else:
                best_sol = sol
                upper = index - 1
            if lower >= upper:
                break
            last_index = index


        return best_sol