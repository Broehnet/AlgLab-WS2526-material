import time

import gurobipy as gp
import networkx as nx
from solution import Solution
from status import Status
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver, UNKNOWN
from heuristics import *
from threading import Timer as ThreadTimer
from pysat.solvers import Solver as SATSolver
import math


class ASSGurobi:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = gp.Model()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.x = {}
        self.nodes = list(self.graph.nodes)
        # decision variables
        for node in self.nodes:
            for i in range(1, self.best):
                self.x[(node, i)] = self.model.addVar(vtype=gp.GRB.BINARY, name=f"x_{node}_{i}")

        self.y = {i: self.model.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}") for i in range(1, self.best)}
        for i in range(1, self.best):
            for edge in self.graph.edges:
                self.model.addConstr(self.x[(edge[0], i)] + self.x[(edge[1], i)] <= 1)

        for i in range(1, self.best):
            for node in self.nodes:
                self.model.addConstr(self.x[(node, i)] <= self.y[i])

        for node in self.nodes:
            self.model.addConstr(gp.quicksum(self.x[(node, i)] for i in range(1, self.best)) == 1)


        self.model.setObjective(gp.quicksum(self.y[i] for i in range(1, self.best)), gp.GRB.MINIMIZE)


    def solve(self, timelimit: float = math.inf):
        if timelimit < math.inf:
            self.model.Params.TimeLimit = timelimit

        self.model.optimize()

        status = self.model.status
        if status == gp.GRB.OPTIMAL or self.model.SolCount > 0:
            self.lower_bound = self.model.objBound
            if status == gp.GRB.OPTIMAL:
                self.status = Status.OPTIMAL
            else:
                self.status = Status.FEASIBLE
            for node in self.nodes:
                for i in range(1, self.best):
                    val = self.x[(node, i)].X
                    if val > 0.5:
                        self.coloring[node] = i
                        break
            self.num_colors = 0
            for i in range(1, self.best):
                if self.y[i].X > 0.5:
                    self.num_colors += 1
            self.upper_bound = self.num_colors
        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound, status=self.status)


class ASSCPSAT:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.solver = CpSolver()
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = CpModel()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.x = {}
        self.nodes = list(self.graph.nodes)
        # decision variables
        for node in self.nodes:
            for i in range(1, self.best):
                self.x[(node, i)] = self.model.new_bool_var(f"x_{node}_{i}")

        self.y = {i: self.model.new_bool_var(f"y_{i}") for i in range(1, self.best)}
        for i in range(1, self.best):
            for edge in self.graph.edges:
                self.model.add(self.x[(edge[0], i)] + self.x[(edge[1], i)] <= 1)

        for i in range(1, self.best):
            for node in self.nodes:
                self.model.add(self.x[(node, i)] <= self.y[i])

        for node in self.nodes:
            self.model.add(sum(self.x[(node, i)] for i in range(1, self.best)) == 1)


        self.model.minimize(sum(self.y[i] for i in range(1, self.best)))


    def solve(self, timelimit: float = math.inf):
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit

        status = self.solver.solve(self.model)

        if status == FEASIBLE or status == OPTIMAL:
            for node in self.nodes:
                for i in range(1, self.best):
                    if self.solver.Value(self.x[(node, i)]):
                        self.coloring[node] = i
                        break
            self.num_colors = 0
            for i in range(1, self.best):
                if self.solver.Value(self.y[i]):
                    self.num_colors += 1
            self.upper_bound = self.num_colors
            if status == OPTIMAL:
                self.status = Status.OPTIMAL
                self.lower_bound = self.upper_bound
            else:
                self.lower_bound = self.solver.BestObjectiveBound()
                self.status = Status.FEASIBLE

        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound, status=self.status)


class ASSSGurobi:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = gp.Model()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.x = {}
        self.nodes = list(self.graph.nodes)
        # decision variables
        for node in self.nodes:
            for i in range(1, self.best):
                self.x[(node, i)] = self.model.addVar(vtype=gp.GRB.BINARY, name=f"x_{node}_{i}")

        self.y = {i: self.model.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}") for i in range(1, self.best)}
        for i in range(1, self.best):
            for edge in self.graph.edges:
                self.model.addConstr(self.x[(edge[0], i)] + self.x[(edge[1], i)] <= 1)

        for i in range(1, self.best):
            for node in self.nodes:
                self.model.addConstr(self.x[(node, i)] <= self.y[i])

        for node in self.nodes:
            self.model.addConstr(gp.quicksum(self.x[(node, i)] for i in range(1, self.best)) == 1)

        for i in range(2, self.best):
            self.model.addConstr(self.y[i] <= self.y[i-1])

        for i in range(1, self.best):
            self.model.addConstr(self.y[i] <= gp.quicksum(self.x[(node, i)] for node in self.nodes))

        self.model.setObjective(gp.quicksum(self.y[i] for i in range(1, self.best)), gp.GRB.MINIMIZE)


    def solve(self, timelimit: float = math.inf):
        if timelimit < math.inf:
            self.model.Params.TimeLimit = timelimit

        self.model.optimize()

        status = self.model.status
        if status == gp.GRB.OPTIMAL or self.model.SolCount > 0:
            self.lower_bound = self.model.objBound
            if status == gp.GRB.OPTIMAL:
                self.status = Status.OPTIMAL
            else:
                self.status = Status.FEASIBLE
            for node in self.nodes:
                for i in range(1, self.best):
                    val = self.x[(node, i)].X
                    if val > 0.5:
                        self.coloring[node] = i
                        break
            self.num_colors = 0
            for i in range(1, self.best):
                if self.y[i].X > 0.5:
                    self.num_colors += 1
            self.upper_bound = self.num_colors
        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound, status=self.status)


class ASSSCPSAT:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.solver = CpSolver()
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = CpModel()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.x = {}
        self.nodes = list(self.graph.nodes)
        # decision variables
        for node in self.nodes:
            for i in range(1, self.best):
                self.x[(node, i)] = self.model.new_bool_var(f"x_{node}_{i}")

        self.y = {i: self.model.new_bool_var(f"y_{i}") for i in range(1, self.best)}
        for i in range(1, self.best):
            for edge in self.graph.edges:
                self.model.add(self.x[(edge[0], i)] + self.x[(edge[1], i)] <= 1)

        for i in range(1, self.best):
            for node in self.nodes:
                self.model.add(self.x[(node, i)] <= self.y[i])

        for node in self.nodes:
            self.model.add(sum(self.x[(node, i)] for i in range(1, self.best)) == 1)

        for i in range(2, self.best):
            self.model.add(self.y[i] <= self.y[i-1])

        for i in range(1, self.best):
            self.model.add(self.y[i] <= sum(self.x[(node, i)] for node in self.nodes))

        self.model.minimize(sum(self.y[i] for i in range(1, self.best)))


    def solve(self, timelimit: float = math.inf):
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit

        status = self.solver.solve(self.model)

        if status == FEASIBLE or status == OPTIMAL:
            for node in self.nodes:
                for i in range(1, self.best):
                    if self.solver.Value(self.x[(node, i)]):
                        self.coloring[node] = i
                        break
            self.num_colors = 0
            for i in range(1, self.best):
                if self.solver.Value(self.y[i]):
                    self.num_colors += 1
            self.upper_bound = self.num_colors
            if status == OPTIMAL:
                self.status = Status.OPTIMAL
                self.lower_bound = self.upper_bound
            else:
                self.lower_bound = self.solver.BestObjectiveBound()
                self.status = Status.FEASIBLE

        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound, status=self.status)


class REPGurobi:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = gp.Model()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.x = {}
        self.nodes = list(self.graph.nodes)
        self.neighbors = {u: list(self.graph.neighbors(u)) for u in self.nodes}
        for u in self.nodes:
            for v in self.nodes:
                if v in self.neighbors[u]:
                    continue
                self.x[(u, v)] = self.model.addVar(vtype=gp.GRB.BINARY, name=f"x_{u}_{v}")

        for u in self.nodes:
            self.model.addConstr(gp.quicksum(self.x[u, v] for v in self.nodes if v not in self.neighbors[u]) == 1)

        self.model.addConstr(gp.quicksum(self.x[u, u] for u in self.nodes) <= best)

        for w in self.nodes:
            excluded = self.neighbors[w] + [w]
            for u, v in self.graph.edges:
                if u in excluded or v in excluded:
                    if u not in excluded:
                        self.model.addConstr(self.x[u, w] <= self.x[w, w])
                    elif v not in excluded:
                            self.model.addConstr(self.x[v, w] <= self.x[w, w])
                else:
                    self.model.addConstr(self.x[(u, w)] + self.x[(v, w)] <= self.x[(w, w)])

        self.model.setObjective(gp.quicksum(self.x[u, u] for u in self.nodes), gp.GRB.MINIMIZE)

    def solve(self, timelimit: float = math.inf):
        if timelimit < math.inf:
            self.model.Params.TimeLimit = timelimit

        self.model.optimize()

        status = self.model.status
        if status == gp.GRB.OPTIMAL or self.model.SolCount > 0:
            self.lower_bound = self.model.objBound
            if status == gp.GRB.OPTIMAL:
                self.status = Status.OPTIMAL
            else:
                self.status = Status.FEASIBLE
            counter = 1
            for u in self.nodes:
                if self.x[u, u].X > 0.5:
                    self.coloring[u] = counter
                    counter += 1
            for u in self.nodes:
                for v in self.nodes:
                    if u == v or u in self.neighbors[v]:
                        continue
                    if self.x[v, u].X > 0.5:
                        self.coloring[v] = self.coloring[u]
            self.num_colors = counter-1
            self.upper_bound = self.num_colors
        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound,
                        status=self.status)


class REPCPSAT:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.solver = CpSolver()
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = CpModel()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.x = {}
        self.nodes = list(self.graph.nodes)
        self.neighbors = {u: list(self.graph.neighbors(u)) for u in self.nodes}
        for u in self.nodes:
            for v in self.nodes:
                if v in self.neighbors[u]:
                    continue
                self.x[(u, v)] = self.model.new_bool_var(f"x_{u}_{v}")

        self.model.add(sum(self.x[u, u] for u in self.nodes) <= best)

        for u in self.nodes:
            self.model.add(sum(self.x[u, v] for v in self.nodes if v not in self.neighbors[u]) == 1)

        for w in self.nodes:
            excluded = self.neighbors[w] + [w]
            for u, v in self.graph.edges:
                if u in excluded or v in excluded:
                    if u not in excluded:
                        self.model.add(self.x[u, w] <= self.x[w, w])
                    elif v not in excluded:
                            self.model.add(self.x[v, w] <= self.x[w, w])
                else:
                    self.model.add(self.x[(u, w)] + self.x[(v, w)] <= self.x[(w, w)])

        self.model.minimize(sum(self.x[u, u] for u in self.nodes))

    def solve(self, timelimit: float = math.inf):

        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit

        status = self.solver.solve(self.model)

        if status == FEASIBLE or status == OPTIMAL:
            counter = 1
            for u in self.nodes:
                    if self.solver.Value(self.x[(u, u)]):
                        self.coloring[u] = counter
                        counter += 1
            self.num_colors = 0
            for u in self.nodes:
                for v in self.nodes:
                    if u == v or u in self.neighbors[v]:
                        continue
                    if self.solver.Value(self.x[(u, u)]):
                        self.coloring[v] = self.coloring[u]
            self.num_colors = counter - 1
            self.upper_bound = self.num_colors
            if status == OPTIMAL:
                self.status = Status.OPTIMAL
                self.lower_bound = self.upper_bound
            else:
                self.lower_bound = self.solver.BestObjectiveBound()
                self.status = Status.FEASIBLE

        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound,
                        status=self.status)


class CPUnequal:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.solver = CpSolver()
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = CpModel()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.nodes = list(self.graph.nodes)
        self.z = {node: self.model.new_int_var(1, best, f"z_{node}") for node in self.nodes}
        z_max = self.model.new_int_var(1, best, "z_max")

        for u, v in self.graph.edges:
            self.model.add(self.z[u] != self.z[v])

        for node in self.nodes:
            self.model.add(self.z[node] <= z_max)

        self.model.minimize(z_max)


    def solve(self, timelimit: float = math.inf):

        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit

        status = self.solver.solve(self.model)

        if status == FEASIBLE or status == OPTIMAL:
            self.num_colors = None
            for u in self.nodes:
                val = self.solver.Value(self.z[u])
                self.coloring[u] = val
                if self.num_colors is None or self.num_colors < val:
                    self.num_colors = val
            self.upper_bound = self.num_colors
            if status == OPTIMAL:
                self.status = Status.OPTIMAL
                self.lower_bound = self.upper_bound
            else:
                self.lower_bound = self.solver.BestObjectiveBound()
                self.status = Status.FEASIBLE

        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound,
                        status=self.status)


class AllDifferent:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.solver = CpSolver()
        self.status = Status.UNKNOWN
        self.num_colors = None
        self.coloring = {}
        self.lower_bound = None
        self.upper_bound = None
        self.model = CpModel()
        self.solution = None
        self.graph = graph
        self.bound = None
        self.best = best + 1
        if not self.best:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.nodes = list(self.graph.nodes)
        self.z = {node: self.model.new_int_var(1, best, f"z_{node}") for node in self.nodes}
        self.z_max = self.model.new_int_var(1, best, "z_max")

        for u, v in self.graph.edges:
            self.model.add(self.z[u] != self.z[v])

        for node in self.nodes:
            self.model.add(self.z[node] <= self.z_max)

        max_num_cliques = len(self.nodes)
        size = 5
        cliques = []
        for i, clique in enumerate(nx.find_cliques(self.graph)):
            if len(clique) <= size:
                continue
            cliques.append(clique)
            if max_num_cliques == i:
                break

        for clique in cliques:
            self.model.add_all_different([self.z[v] for v in clique])
        self.model.minimize(self.z_max)


    def solve(self, timelimit: float = math.inf):

        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit

        status = self.solver.solve(self.model)

        if status == FEASIBLE or status == OPTIMAL:
            self.num_colors = None
            for u in self.nodes:
                val = self.solver.Value(self.z[u])
                self.coloring[u] = val
                if self.num_colors is None or self.num_colors < val:
                    self.num_colors = val
            self.upper_bound = self.num_colors
            if status == OPTIMAL:
                self.status = Status.OPTIMAL
                self.lower_bound = self.upper_bound
            else:
                self.lower_bound = self.solver.BestObjectiveBound()
                self.status = Status.FEASIBLE

        else:
            self.upper_bound = math.inf
            self.lower_bound = -math.inf
            self.coloring = {}

        return Solution(coloring=self.coloring, num_colors=self.upper_bound, lower_bound=self.lower_bound,
                        status=self.status)

class PYSATDecisionVariant:

    def __init__(self, graph: nx.Graph, k, timelimit: float = math.inf):
        self.status = None
        self.solver = SATSolver("Minicard")
        self.timeout = False
        def interrupt(_):
            self.solver.interrupt()
            self.timeout = True
        self.timelimit_provided = False
        if timelimit is not None:
            if timelimit < math.inf:
                self.timer = ThreadTimer(timelimit, interrupt, [None])
                self.timer.start()
                self.timelimit_provided = True
        self.k = k
        self.graph = graph
        self.nodes = list(self.graph.nodes)
        self.var = {}
        self.var_count = 1
        self.coloring = {}
        for node in self.nodes:
            clause = []
            for i in range(1, k+1):
                self.var[(node, i)] = self.var_count
                clause.append(self.var_count)
                self.var_count += 1
            self.solver.add_clause(clause)
        self.node_color = {var: node_color for node_color, var in self.var.items()}

        for u, v in self.graph.edges:
            for i in range(1, k+1):
                self.solver.add_clause([-self.var[(u, i)], -self.var[(v, i)]])


    def solve(self):
        self.status = self.solver.solve_limited(expect_interrupt=self.timelimit_provided)
        if not self.status:
            return None, self.status
        true_vars = {var for var in self.solver.get_model() if var > 0}
        for var in true_vars:
            node, color = self.node_color[var]
            self.coloring[node] = color
        return self.coloring, self.status


class PYSATSolver:

    def __init__(self, graph: nx.Graph, best: int = -1):
        self.status = None
        self.graph = graph
        self.best = best
        if self.best == -1:
            self.best = max(dict(self.graph.degree).values()) + 1
        self.best_sol = None


    def solve(self, timelimit: float = math.inf):
        timing = False
        start = None
        if timelimit < math.inf:
            start = time.time()
            timing = True
        k = self.best
        status = None
        timeout = False
        while True:
            remaining = None
            if timing:
                runtime = time.time() - start
                if runtime > timelimit:
                    timeout = True
                    break
                remaining = timelimit - runtime
            decision_variant = PYSATDecisionVariant(self.graph, k, remaining)
            sol, status = decision_variant.solve()
            if decision_variant.timeout:
                timeout = True
            if not status:
                break
            self.best_sol = sol
            self.best = k
            k -= 1
            if not k:
                break

        if self.best_sol is None:
            if timeout:
                self.status = Status.UNKNOWN
            else:
                self.status = Status.INFEASIBLE
        else:
            if timeout:
                self.status = Status.FEASIBLE
            else:
                self.status = Status.OPTIMAL

        return Solution(coloring=self.best_sol, num_colors=self.best, lower_bound=None,
                        status=self.status)








