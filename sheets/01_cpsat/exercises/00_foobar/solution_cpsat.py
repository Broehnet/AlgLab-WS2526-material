from data_schema import Instance, Solution
from ortools.sat.python import cp_model


def solve(instance: Instance) -> Solution:
    """
    Implement your solver for the problem here!
    """
    numbers = instance.numbers
    model = cp_model.CpModel()
    domain1 = cp_model.Domain.from_values(numbers)
    x1 = model.new_int_var_from_domain(domain1, "x1")
    x2 = model.new_int_var_from_domain(domain1, "x2")

    #Variante 1
    absx1x2 = model.new_int_var(0, abs(max(numbers, key=abs))*2, "absx1x2")
    model.add_abs_equality(target=absx1x2, expr=x2-x1)
    model.maximize(absx1x2)

    #Variante  2
    # model.add(x2 >= x1)
    # model.maximize(x2 - x1)

    solver = cp_model.CpSolver()
    solver.solve(model)
    return Solution(
        number_a=solver.Value(x1),
        number_b=solver.Value(x2),
        # distance=solver.Value(x2) - solver.Value(x1),
        distance=solver.Value(absx1x2),
    )
