import unittest

import numpy as np

from leontief import inverse, matvec, productivity_bounds, solve, system_matrix


class LeontiefTests(unittest.TestCase):
    def setUp(self):
        self.inputs = [[.2, .1, .1], [.1, .2, .1], [.1, .1, .2]]
        self.matrix = system_matrix(self.inputs)
        self.demand = [66, 48, 30]

    def test_hand_calculation(self):
        np.testing.assert_allclose(solve(self.matrix, self.demand), [100, 80, 60])
        np.testing.assert_allclose(
            matvec(inverse(self.matrix), self.demand), [100, 80, 60],
        )

    def test_singular_and_zero_cases(self):
        with self.assertRaises(ValueError):
            solve([[0]], [1])
        with self.assertRaises(ValueError):
            inverse([[0]])
        self.assertEqual(productivity_bounds([[0]]), (0, 0))
        self.assertEqual(productivity_bounds([[1]]), (1, 1))

    def test_numpy_comparison(self):
        matrix = [[0, 1], [2, 3]]
        np.testing.assert_allclose(solve(matrix, [5, 7]), np.linalg.solve(matrix, [5, 7]))
        np.testing.assert_allclose(inverse(matrix), np.linalg.inv(matrix))
        inputs = [[0, .8], [.2, 0]]
        lower, upper = productivity_bounds(inputs)
        expected = max(abs(np.linalg.eigvals(inputs)))
        self.assertLessEqual(lower - 1e-12, expected)
        self.assertGreaterEqual(upper + 1e-12, expected)
        self.assertLess(upper - lower, 1e-8)


if __name__ == "__main__":
    unittest.main()
