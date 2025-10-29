from data_schema import Instance, Solution


def solve(instance: Instance) -> Solution:
    """
    Implement your solver for the problem here!
    """
    numbers = instance.numbers
    smallest = numbers[0]
    biggest = numbers[0]
    for number in numbers:
        if number < smallest:
            smallest = number
        if number > biggest:
            biggest = number
    return Solution(
        number_a=smallest,
        number_b=biggest,
        distance=abs(smallest - biggest),
    )
