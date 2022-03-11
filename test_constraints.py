##
# test_constraints.py
# Unit tests for constraints.py.
##


import unittest
from constraints import get_constraints, MembershipConstraint, EqualityConstraint
from naive import reduction, expected_reduction, best_expected_reduction

class TestConstraints(unittest.TestCase):

    def test_constraints1(self):
        self.assertEqual(set([MembershipConstraint('C', set()),
                              MembershipConstraint('R', set()),
                              MembershipConstraint('A', {0, 1, 3, 4}),
                              MembershipConstraint('N', {0, 1, 2, 4}),
                              EqualityConstraint('E', 4)]),
                         get_constraints("CRANE", "NAIVE"))

    def test_permits_method(self):
        constraint = MembershipConstraint('A', {0, 1, 3, 4})
        self.assertEqual(constraint.permits("CRANE"), False)
        self.assertEqual(constraint.permits("ALERT"), True)
        self.assertEqual(constraint.permits("ALOHA"), True)
        self.assertEqual(constraint.permits("AMAZE"), False)
        self.assertEqual(constraint.permits("CRONY"), False)


    def test_reduction(self):
        pool = ["ALERT", "ALOHA", "NAIVE", "CRONY", "ANODE"]
        self.assertEqual(reduction("CRANE", "NAIVE", pool), 0.4)
        self.assertEqual(reduction("CRANE", "ALERT", pool), 0.2)
        self.assertEqual(reduction("CRANE", "ALOHA", pool), 0.2)
        self.assertEqual(reduction("CRANE", "CRONY", pool), 0.2)
        self.assertEqual(reduction("CRANE", "ANODE", pool), 0.4)

    def test_expected_reduction(self):
        pool = ["ALERT", "ALOHA", "NAIVE", "CRONY", "ANODE"]
        self.assertAlmostEqual(expected_reduction("CRANE", pool, pool), 0.28)
        self.assertAlmostEqual(expected_reduction("CRANE", ["ALERT", "ALOHA"], pool), 0.2)
        self.assertAlmostEqual(expected_reduction("CRANE", ["ALERT", "ANODE"], pool), 0.3)

    def test_expected_reduction2(self):
        pool = ["ABBBB", "CDCCC", "EEFEE", "GGGHG", "BDFHG"]
        self.assertAlmostEqual(expected_reduction("ABBBB", pool, pool), 0.44)
        self.assertAlmostEqual(expected_reduction("CDCCC", pool, pool), 0.44)
        self.assertAlmostEqual(expected_reduction("EEFEE", pool, pool), 0.44)
        self.assertAlmostEqual(expected_reduction("GGGHG", pool, pool), 0.44)
        self.assertAlmostEqual(expected_reduction("BDFHG", pool, pool), 0.2)

    def test_best_expected_reduction(self):
        pool = ["ABBBB", "CDCCC", "EEFEE", "GGGHG", "BDFHG"]
        self.assertEqual(best_expected_reduction(pool, pool), "BDFHG")


if __name__ == "__main__":
    unittest.main()   