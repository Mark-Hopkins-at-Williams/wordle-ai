##
# test_infomax.py
# Unit tests for infomax.py.
##


import unittest
from infomax import split_pool, expectation
from play import update_pool

class TestInfomax(unittest.TestCase):

    def test_split_pool(self):
        pool = ["CRANE", "CRATE", "PLANE", "ANODE", "PANIC"]
        green, yellow, gray = split_pool(pool, "N", 3)
        self.assertEqual(set(green), set(['CRANE', 'PLANE']))
        self.assertEqual(set(yellow), set(['ANODE', 'PANIC']))
        self.assertEqual(set(gray), set(['CRATE']))

    def test_expectation(self):
        pool = ["AD", "AT", "AX", "ID", "TO", "TI"]
        self.assertAlmostEqual(expectation("TI", pool), 4/3)
        self.assertAlmostEqual(expectation("TO", pool), 2)


    def test_update_pool(self):
        pool = ["AD", "AT", "AX", "ID", "TO", "TI"]
        updated_pool = update_pool(guess="TO", target="AX", pool=pool)
        self.assertEqual(set(updated_pool), set(["AD", "AX", "ID"]))
        updated_pool = update_pool(guess="DE", target="AD", pool=pool)
        self.assertEqual(set(updated_pool), set(["AD", "ID"]))


if __name__ == "__main__":
    unittest.main()   