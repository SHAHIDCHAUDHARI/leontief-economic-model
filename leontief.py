"""Core calculations for a non-negative Leontief input matrix."""

from math import isfinite


def system_matrix(inputs):
    return [
        [int(row == column) - coefficient for column, coefficient in enumerate(values)]
        for row, values in enumerate(inputs)
    ]


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def eliminate(matrix, right, *, trace=None):
    """Row-reduce [matrix | right] with partial pivoting."""
    size = len(matrix)
    augmented = [list(row) + list(rhs) for row, rhs in zip(matrix, right)]
    if trace is not None:
        trace.append(("Starting augmented matrix", [row.copy() for row in augmented]))

    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("I − A is singular or too close to singular to solve reliably.")
        operations = []
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
            operations.append(f"Swap R{column + 1} and R{pivot + 1}.")
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        operations.append(f"Divide R{column + 1} by {divisor:.6g}.")

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
            operations.append(f"R{row + 1} ← R{row + 1} − ({factor:.6g}) × R{column + 1}.")
        if trace is not None:
            trace.append((" ".join(operations), [row.copy() for row in augmented]))

    return [row[size:] for row in augmented]


def solve(matrix, demand, *, trace=None):
    result = eliminate(matrix, [[value] for value in demand], trace=trace)
    return [row[0] for row in result]


def inverse(matrix):
    size = len(matrix)
    identity = [[int(row == column) for column in range(size)] for row in range(size)]
    return eliminate(matrix, identity)


def productivity_bounds(inputs, iterations=300):
    """Bound rho(A) using ratios from a positive vector and shifted power iteration."""
    vector = [1.0] * len(inputs)
    lower, upper = 0.0, float("inf")
    for _ in range(iterations):
        product = matvec(inputs, vector)
        ratios = [value / current for value, current in zip(product, vector)]
        lower = max(lower, min(ratios))
        upper = min(upper, max(ratios))
        if upper - lower <= 1e-9:
            break
        shifted = [value + current for value, current in zip(product, vector)]
        scale = max(shifted)
        vector = [max(value / scale, 1e-100) for value in shifted]
    return lower, upper


def validate_inputs(inputs, demand):
    if any(not isfinite(value) or value < 0 for row in inputs for value in row):
        raise ValueError("Input rates must be finite and non-negative.")
    if any(not isfinite(value) or value < 0 for value in demand):
        raise ValueError("Final demands must be finite and non-negative.")
