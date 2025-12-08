import math

import networkx as nx

from solution import Solution


class DegreeBasedPreprocessor:
    """
    A preprocessor that removes low-degree vertices from the graph.
    This needs to be a class as it maintains state between the preprocessing and postprocessing steps.
    """
    def __init__(self, graph: nx.Graph):
        self.graph = graph  # the original graph
        self.l = nx.approximation.large_clique_size(self.graph)
        self.removed = []


    def preprocess(self) -> nx.Graph:
        G = self.graph.copy()
        low_deg = [node for node, deg in G.degree() if deg < self.l]
        while True:
            if not low_deg:
                break
            node = low_deg.pop()
            neighbors = G.neighbors(node)
            G.remove_node(node)
            self.removed.append(node)
            for n in neighbors:
                if G.degree(n) < self.l and n not in low_deg:
                    low_deg.append(n)
        return G


    def postprocess(self, solution: Solution) -> Solution:
        coloring = solution.coloring
        num_colors = solution.num_colors
        if num_colors != math.inf:
            for node in reversed(self.removed):
                numbers = {coloring[u] for u in self.graph.neighbors(node) if u in coloring}
                for i in range(1, num_colors+1):
                    if i not in numbers:
                        coloring[node] = i
                        break

        return Solution(coloring=coloring, num_colors=num_colors, lower_bound=solution.lower_bound, status=solution.status)


