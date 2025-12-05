import networkx as nx
import random

from networkx.classes import neighbors


def naive_greedy(graph: nx.Graph):
    nodes_by_degree = sorted(list(graph.nodes), key=lambda n: graph.degree(n), reverse=True)
    return greedy(graph, nodes_by_degree)


def multi_start_greedy(graph: nx.Graph, rounds):
    if rounds < 1:
        return -1
    nodelist = list(graph.nodes)
    smallest = None
    for i in range(rounds):
        random.shuffle(nodelist)
        current = greedy(graph, nodelist.copy())
        if smallest is None or current[1] < smallest[1]:
            smallest = current
    return smallest


def greedy(graph: nx.Graph, nodelist):
    coloring = {}
    for node in nodelist:
        neighbor_colors = {coloring[n] for n in graph.neighbors(node) if n in coloring}
        k = 1
        while True:
            if k not in neighbor_colors:
                break
            k += 1
        coloring[node] = k
    return coloring, max(coloring.values())


def dsatur(graph: nx.Graph):
    coloring = {}
    deg = {node: graph.degree(node) for node in graph.nodes}
    sat = {node: set() for node in graph.nodes}
    for _ in range(len(list(graph.nodes))):
        most_sat = None
        most_deg = None
        best_node = None
        for node in graph.nodes:
            if node in coloring:
                continue
            current_sat = len(sat[node])
            current_deg = deg[node]
            if most_sat is None or most_sat < current_sat:
                most_sat = current_sat
                most_deg = current_deg
                best_node = node
            elif most_sat == current_sat and current_deg > most_deg:
                most_deg = current_deg
                best_node = node
        k = 1
        colors = sat[best_node]
        while True:
            if not k in colors:
                break
            k += 1
        coloring[best_node] = k
        neighbors = graph.neighbors(best_node)
        for n in neighbors:
            if n not in coloring:
                sat[n].add(k)

    return coloring, max(coloring.values())


G = nx.erdos_renyi_graph(n=1000, p=.5)

print(naive_greedy(G)[1])
print(multi_start_greedy(G, 10)[1])
print(dsatur(G)[1])