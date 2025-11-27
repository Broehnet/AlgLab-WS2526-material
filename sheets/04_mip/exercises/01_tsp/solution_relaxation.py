"""
Implement the Dantzig-Fulkerson-Johnson formulation for the TSP.
"""

import logging
import typing

import gurobipy as gp
import networkx as nx


class GurobiTspRelaxationSolver:
    """
    IMPLEMENT ME!
    """

    def __init__(self, G: nx.Graph, k: int = 2):
        """
        G is a weighted networkx graph, where the weight of an edge is stored in the
        "weight" attribute. It is strictly positive.
        """
        self.graph = G
        self.k = k
        assert (
            G.number_of_edges() == G.number_of_nodes() * (G.number_of_nodes() - 1) / 2
        ), "Invalid graph"
        assert all(
            weight > 0
            for _, _, weight in G.edges.data("weight", default=None)  # type: ignore[attr-defined]
        ), "Invalid graph"
        assert k in {1, 2}, "Invalid k"
        logging.info("Creating model ...")
        logging.info(
            "Graph has %d nodes and %d edges", G.number_of_nodes(), G.number_of_edges()
        )
        logging.info("Implementing subtour elimination with >= %d", k)
        self._model = gp.Model()
        # TODO: Implement me!
        self.vars = {(u, v): self._model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0.0, ub=1.0, name=f"{u}_{v}") for u, v in self.graph.edges}
        for u in self.graph.nodes:
            self._model.addConstr(gp.quicksum(self.x(u, v) for v in self.graph.nodes if v != u) == 2)
        self._model.setObjective(sum(self.graph[u][v]["weight"] * x for (u, v), x in self.vars.items()), gp.GRB.MINIMIZE)
        self.solution = None


    def x(self, u, v):
        if (u, v) in self.vars:
            return self.vars[(u, v)]
        return self.vars[(v, u)]


    def get_lower_bound(self) -> float:
        """
        Return the current lower bound.
        """
        # TODO: Implement me!
        return self._model.ObjBound

    def get_solution(self) -> typing.Optional[nx.Graph]:
        """
        Return the current solution as a graph.

        The solution should be a networkx Graph were the
        fractional value of the edge is stored in the "x" attribute.
        You do not have to add edges with x=0.

        ```python
        graph = nx.Graph()
        graph.add_edge(0, 1, x=0.5)
        graph.add_edge(1, 2, x=1.0)
        ```
        """
        return self.solution

    def get_objective(self) -> typing.Optional[float]:
        """
        Return the objective value of the last solution.
        """
        # TODO: Implement me!
        return sum(self.graph[u][v]["weight"]*x.X for (u, v), x in self.vars.items() if x.X >= 0.01)

    def solve(self) -> None:
        """
        Solve the model. After solving the model, the solution, its objective value,
        and the lower bounds should be available via the corresponding methods.
        """
        logging.info("Solving model ...")
        # Set parameters for the solver.
        self._model.Params.LogToConsole = 1
        while True:
            self._model.optimize()
            if self._model.status == gp.GRB.INFEASIBLE:
                break
            if self._model.status == gp.GRB.OPTIMAL:
                G = nx.Graph()
                for u, v in self.graph.edges:
                    x = self.x(u, v)
                    if x.X >= 0.01:
                        G.add_edge(u, v, weight=self.graph[u][v]["weight"], x=x.X)
                comps = list(nx.connected_components(G))
                if len(comps) == 1:
                    self.solution = G
                    break
                for comp in comps:
                    not_in_comp = [u for u in self.graph if u not in comp]
                    outgoing = []
                    for u in comp:
                        outgoing += [self.x(u, v) for v in not_in_comp]
                    self._model.addConstr(gp.quicksum(outgoing) >= self.k)