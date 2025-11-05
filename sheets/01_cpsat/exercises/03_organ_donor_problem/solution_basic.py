import math

import networkx as nx
from data_schema import Donation, Solution
from database import TransplantDatabase
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver


def create_graph(database: TransplantDatabase):
    g = nx.MultiDiGraph()
    recipients = database.get_all_recipients()
    for recipient in recipients:
        g.add_node(recipient.id)
    pairs = [(donor, database.get_partner_recipient(donor)) for donor in database.get_all_donors()]
    for donor, recipient in pairs:
        compatible_recipients = database.get_compatible_recipients(donor)
        for comp in compatible_recipients:
            if recipient != comp:
                g.add_edge(recipient.id, comp.id, donor=donor.id)
    while True:
        remove = [r for r in g.nodes if g.in_degree(r) == 0 or g.out_degree(r) == 0]
        if len(remove) == 0:
            break
        g.remove_nodes_from(remove)
    return g


class CrossoverTransplantSolver:
    def __init__(self, database: TransplantDatabase) -> None:
        """
        Constructs a new solver instance, using the instance data from the given database instance.
        :param Database database: The organ donor/recipients database.
        """
        self.database = database
        # TODO: Implement me!
        self.model = CpModel()
        self.graph = create_graph(self.database)
        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        self.x = {(r1, r2, donor): self.model.new_bool_var(f"x_{r1}_{r2}_{donor}") for r1, r2, donor in self.graph.edges(data='donor')}

        # constraints
        # 1 donor
        for donor in database.get_all_donors():
            self.model.add(sum(self.x[(r1, r2, d)] for r1, r2, d in self.x if donor.id == d) <= 1)

        # 1 recipient
        for recipient in self.graph.nodes:
            self.model.add(sum(self.x[(r1, r2, donor)] for r1, r2, donor in self.graph.in_edges(recipient, 'donor')) <= 1)

        # A donor is willing to donate only if their associated recipient receives an organ in exchange.
        # for donor in self.database.get_all_donors():
        #     recipient = self.database.get_partner_recipient(donor)
        #     if recipient.id not in self.graph.nodes:
        #         continue
        #     donations = [self.x[(r1, r2, d)] for r1, r2, d in self.graph.in_edges(recipient.id, 'donor')]
        #     for r1, r2, d in self.x:
        #         if d == donor.id:
        #             self.model.add_bool_or(*donations, ~self.x[(r1, r2, d)])
        for recipient in self.graph.nodes:
            in_edges = self.graph.in_edges(recipient, 'donor')
            out_edges = self.graph.out_edges(recipient, 'donor')
            self.model.add(sum(self.x[(r1, r2, donor)] for r1, r2, donor in out_edges) == sum(self.x[(r1, r2, donor)] for r1, r2, donor in in_edges))





        # If a recipient has multiple willing donors, only one of them is willing to donate in the final solution.
        for recipient in self.graph.nodes:
            self.model.add(sum(self.x[(r1, r2, d)] for r1, r2, d in self.graph.out_edges(recipient, 'donor')) <= 1)

        # objective
        self.model.maximize(sum(self.x.values()))







    def optimize(self, timelimit: float = math.inf) -> Solution:
        """
        Solves the constraint programming model and returns the optimal solution (if found within time limit).
        :param timelimit: The maximum time limit for the solver.
        :return: A list of Donation objects representing the best solution, or None if no solution was found.
        """
        if timelimit <= 0.0:
            return Solution(donations=[])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!
        self.solver.solve(self.model)
        result = []
        r_by_id = {r.id: r for r in self.database.get_all_recipients()}
        d_by_id = {d.id: d for d in self.database.get_all_donors()}
        for (r1, r2, donor), value in self.x.items():
            if self.solver.value(value):
                result.append(Donation(donor=d_by_id[donor], recipient=r_by_id[r2]))
        return Solution(donations=result)

