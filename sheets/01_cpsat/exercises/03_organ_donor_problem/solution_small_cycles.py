import math
from collections import defaultdict

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


class CycleLimitingCrossoverTransplantSolver:
    def __init__(self, database: TransplantDatabase) -> None:
        """
        Constructs a new solver instance, using the instance data from the given database instance.
        :param Database database: The organ donor/recipients database.
        """

        self.database = database
        # TODO: Implement me!
        self.model = CpModel()
        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        self.graph = create_graph(self.database)
        self.cycles = list(nx.simple_cycles(self.graph, 3))
        self.x = [self.model.new_bool_var(f"x_{i}") for i in range(len(self.cycles))]

        # constraints
        # each node may only be in one active cycle
        for node in self.graph.nodes:
            cycles = [i for i, cycle in enumerate(self.cycles) if node in cycle]
            self.model.add(sum(self.x[i] for i in cycles) <= 1)

        # objective
        self.model.maximize(sum(self.x[i] * len(cycle) for i, cycle in enumerate(self.cycles)))




    def optimize(self, timelimit: float = math.inf) -> Solution:
        if timelimit <= 0.0:
            return Solution(donations=[])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!
        self.solver.solve(self.model)
        result = []
        r_by_id = {r.id: r for r in self.database.get_all_recipients()}
        d_by_id = {d.id: d for d in self.database.get_all_donors()}
        for i, cycle in enumerate(self.cycles):
            if self.solver.value(self.x[i]):
                pairs = []
                if len(cycle) == 2:
                    pairs = [(cycle[0], cycle[1]), (cycle[1], cycle[0])]
                else:
                    pairs = [(cycle[0], cycle[1]), (cycle[1], cycle[2]), (cycle[2], cycle[0])]
                for pair in pairs:
                    donor_id = self.graph[pair[0]][pair[1]][0]['donor']
                    donor = d_by_id[donor_id]
                    recipient = r_by_id[pair[1]]
                    result.append(Donation(donor=donor, recipient=recipient))

        return Solution(donations=result)
