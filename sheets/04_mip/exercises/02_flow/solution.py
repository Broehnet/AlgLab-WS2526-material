import logging

import gurobipy as gp
import networkx as nx
from data_schema import Instance, Solution
from gurobipy import GRB



class MiningRoutingSolver:
    def __init__(self, instance: Instance) -> None:
        self.instance = instance
        self.budget = instance.budget
        logging.info("Creating model ...")
        logging.info(
            "Instance has %d locations, %d mines, %d tunnels, and a budget of %.2f",
            len(instance.locations),
            len(instance.mines),
            len(instance.tunnels),
            instance.budget,
        )
        # TODO: Implement me!
        # build graph
        self.model = gp.Model()
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(instance.locations, mine=True)
        self.graph.nodes[instance.elevator_location]["mine"] = False
        for loc, mine in self.instance.mines.items():
            self.graph.nodes[loc]["o"] = mine.ore_per_hour
        # variables
        self.x = {}
        self.f = {}
        self.costs = 0
        for tun in self.instance.tunnels:
            self.graph.add_edge(tun.source, tun.target, c=tun.reinforcement_costs, u=tun.throughput_per_hour)
            self.x[(tun.source, tun.target)] = self.model.addVar(vtype=gp.GRB.BINARY, name=f"x_{tun.source}_{tun.target}")
            self.f[(tun.source, tun.target)] = self.model.addVar(lb=0, ub=tun.throughput_per_hour, vtype=gp.GRB.CONTINUOUS, name=f"f_{tun.source}_{tun.target}")
            # other direction
            self.graph.add_edge(tun.target, tun.source, c=tun.reinforcement_costs, u=tun.throughput_per_hour)
            self.x[(tun.target, tun.source)] = self.model.addVar(vtype=gp.GRB.BINARY, name=f"x_{tun.target}_{tun.source}")
            self.f[(tun.target, tun.source)] = self.model.addVar(lb=0, ub=tun.throughput_per_hour, vtype=gp.GRB.CONTINUOUS, name=f"f_{tun.target}_{tun.source}")

            self.costs += (self.x[(tun.source, tun.target)] + self.x[(tun.target, tun.source)]) * tun.reinforcement_costs
            self.model.addConstr(self.x[(tun.source, tun.target)] + self.x[(tun.target, tun.source)] <= 1)
            self.model.addConstr(self.f[(tun.source, tun.target)] <= self.x[(tun.source, tun.target)] * tun.throughput_per_hour)
            self.model.addConstr(self.f[(tun.target, tun.source)] <= self.x[(tun.target, tun.source)] * tun.throughput_per_hour)

        self.model.addConstr(self.costs <= instance.budget)

        for loc in self.graph.nodes:
            incoming = gp.quicksum(self.f[edge] for edge in self.graph.in_edges(loc))
            outgoing = gp.quicksum(self.f[edge] for edge in self.graph.out_edges(loc))

            if self.graph.nodes[loc]["mine"]:
                self.model.addConstr(outgoing - incoming <= self.graph.nodes[loc]["o"])
            else:
                self.model.addConstr(outgoing == 0)

        self.model.setObjective(gp.quicksum(self.f[edge] for edge in self.graph.in_edges(self.instance.elevator_location)), gp.GRB.MAXIMIZE)



    def solve(self) -> Solution:
        """
        Calculate the optimal solution to the problem.
        Returns the "flow" as a list of tuples, each tuple with two entries:
            - The *directed* edge tuple. Both entries in the edge should be ints, representing the ids of locations.
            - The throughput/utilization of the edge, in goods per hour
        """
        # TODO: implement me!
        logging.info("Solving model...")
        self.model.optimize()

        result = []
        for edge, f in self.f.items():
            if f.X >= 0.01:
                result.append((edge, f.X))
        return Solution(flow=result)

