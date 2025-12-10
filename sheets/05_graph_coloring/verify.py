import random

import networkx as nx
import timeit
import pandas as pd
import performance_plot as pp


from preprocessing import DegreeBasedPreprocessor
from solvers import *
from heuristics import dsatur

def test_correctness(graph: nx.Graph, coloring):
    for edge in graph.edges:
        if coloring[edge[0]] == coloring[edge[1]]:
            return False
    return True

def generate_benchmark_set(seed=42):
    graphs = []
    parameters = [6, 9]
    for k in parameters:
        graphs.append((f"mycielsky_{k}", nx.mycielski_graph(k)))

    parameters = [(420, 3), (300, 24)]
    for (n, m) in parameters:
        graphs.append((f"barabasi_albert_{n}_{m}", nx.barabasi_albert_graph(n, m, seed)))

    parameters = [(300, 8), (420, 4)]
    for (n, d) in parameters:
        graphs.append((f"random_regular_{d}_{n}", nx.random_regular_graph(d, n, seed)))

    parameters = [(12, 3), (15, 4)]
    for (n, m) in parameters:
        graphs.append((f"kneser_{n}_{m}", nx.generators.kneser_graph(n, m)))

    parameters = [(300, 0.2), (230, 0.5)]
    for (n, p) in parameters:
        graphs.append((f"erdos_renyi_{n}_{p}", nx.erdos_renyi_graph(n, p, seed)))

    return graphs


def run_tests(graph, Solver, best, Gn, preprocessor, timelimit=60):
    G = graph[1]
    sol = None
    if Gn is None or not Gn.number_of_nodes():
        test_solver = Solver(G, best)
        sol = test_solver.solve(timelimit)
    else:
        test_solver = Solver(Gn, best)
        sol = test_solver.solve(timelimit)
        sol = preprocessor.postprocess(sol)
    result = (graph[0], sol)
    return result

def run_evaluation_solvers(path):
    solvers = [ASSGurobi, ASSCPSAT, ASSSGurobi, ASSSCPSAT, REPGurobi, REPCPSAT, CPUnequal, AllDifferent, PYSATSolver]
    test_set = generate_benchmark_set()
    timelimit = 60
    results = []
    for graph in test_set:
        best = dsatur(graph[1])
        preprocessor = None
        Gn = None
        for solver in solvers:
            if graph[0] == "kneser_15_4" and (solver == REPGurobi or solver == REPCPSAT):
                results.append({"test_graph": graph[0], "solver": solver.__name__, "num_colors": math.inf,
                                "lower_bound": -math.inf})
                continue
            print(solver.__name__, " ", graph[0])
            result = run_tests(graph, solver, best, Gn, preprocessor, timelimit)
            name = result[0]
            sol = result[1]
            results.append({"test_graph": name, "solver": solver.__name__, "num_colors": sol.num_colors,
                            "lower_bound": sol.lower_bound})
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)


def run_evaluation_solvers_and_preprocessing(path):
    solvers = [ASSGurobi, ASSCPSAT, ASSSGurobi, ASSSCPSAT, REPGurobi, REPCPSAT, CPUnequal, AllDifferent, PYSATSolver]
    test_set = generate_benchmark_set()
    timelimit = 60
    results = []
    for graph in test_set:
        best = dsatur(graph[1])
        preprocessor = DegreeBasedPreprocessor(graph[1].copy())
        Gn = preprocessor.preprocess()
        for solver in solvers:
            if graph[0] == "kneser_15_4" and (solver == REPGurobi or solver == REPCPSAT):
                results.append({"test_graph": graph[0], "solver": f"{solver.__name__}_preprocessed", "num_colors": math.inf,
                                "lower_bound": -math.inf})
                continue
            print(solver.__name__, " ", graph[0])
            result = run_tests(graph, solver, best, Gn, preprocessor, timelimit)
            name = result[0]
            sol = result[1]
            results.append({"test_graph": name, "solver": f"{solver.__name__}_preprocessed", "num_colors": sol.num_colors,
                            "lower_bound": sol.lower_bound})
    for graph in test_set:
        best = dsatur(graph[1])
        preprocessor = None
        Gn = None
        for solver in solvers:
            if graph[0] == "kneser_15_4" and (solver == REPGurobi or solver == REPCPSAT):
                results.append({"test_graph": graph[0], "solver": solver.__name__, "num_colors": math.inf,
                                "lower_bound": -math.inf})
                continue
            print(solver.__name__, " ", graph[0])
            result = run_tests(graph, solver, best, Gn, preprocessor, timelimit)
            name = result[0]
            sol = result[1]
            results.append({"test_graph": name, "solver": solver.__name__, "num_colors": sol.num_colors,
                            "lower_bound": sol.lower_bound})
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)


def run_evaluation_heuristics(path):
    test_set = generate_benchmark_set()
    heuristics = [dsatur, naive_greedy, multi_start_greedy]
    results = []
    rounds = 20
    for graph in test_set:
        name = graph[0]
        for heuristic in heuristics:
            sol = None
            if heuristic == multi_start_greedy:
                sol = heuristic(graph[1], rounds)
            else:
                sol = heuristic(graph[1])
            results.append(
                {"test_graph": name, "solver": heuristic.__name__, "num_colors": sol})
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)


def main():
    csv_path_solvers = "evaluation_solvers.csv"
    run_evaluation_solvers(csv_path_solvers)
    csv_path_solvers_and_preprocessing = "evaluation_solvers_and_preprocessing.csv"
    run_evaluation_solvers(csv_path_solvers_and_preprocessing)
    csv_path_solvers_and_preprocessing = "evaluation_heuristics.csv"
    run_evaluation_solvers(csv_path_solvers_and_preprocessing)
    pp.main()


if __name__ == "__main__":
    main()