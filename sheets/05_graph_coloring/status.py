from enum import Enum

class Status(Enum):

    UNKNOWN = 0
    OPTIMAL = 1
    FEASIBLE = 2
    INFEASIBLE = 3