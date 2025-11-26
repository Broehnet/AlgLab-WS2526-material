import itertools

import networkx as nx
from networkx.classes import neighbors
from pysat.solvers import Solver as SATSolver


class HamiltonianCycleModel:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph
        self.solver = SATSolver("Minicard")
        self.assumptions = []
        self.edge_to_var = {}
        self.var_to_edge = {}
        for i, (u, v) in enumerate(self.graph.edges):
            self.edge_to_var[(u, v)] = i+1
            self.edge_to_var[(v, u)] = i+1
            self.var_to_edge[i+1] = (u, v)
        for u in self.graph:
            var_edges = [self.edge_to_var[(u, v)] for v in self.graph.neighbors(u)]
            self.solver.add_atmost(var_edges, 2)
            self.solver.add_clause(var_edges)
            self.solver.add_atmost([-edge for edge in var_edges], len(var_edges)-2)




    def solve(self) -> list[tuple[int, int]] | None:
        """
        Solves the Hamiltonian Cycle Problem. If a HC is found,
        its edges are returned as a list.
        If the graph has no HC, 'None' is returned.
        """
        while True:
            if not self.solver.solve():
                return None
            temp = nx.Graph()
            temp.add_nodes_from(self.graph.nodes)
            edges = []
            for var in self.solver.get_model():
                if var > 0:
                    edges.append(self.var_to_edge[var])
            temp.add_edges_from(edges)
            components = list(nx.connected_components(temp))
            if len(components) == 1:
                return edges
            for component in components:
                outgoing_edges = []
                for u in component:
                    for v in self.graph.neighbors(u):
                        if v not in component:
                            outgoing_edges.append(self.edge_to_var[(u, v)])
                if not outgoing_edges:
                    return None
                self.solver.add_clause(outgoing_edges)












