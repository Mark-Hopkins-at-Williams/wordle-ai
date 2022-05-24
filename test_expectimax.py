##
# test_expectimax.py
# Unit tests for expectimax.py.
##

import unittest
from expectimax import max_layer

class TestInfomax(unittest.TestCase):

    def test_update_pool(self):
        pool = ["AD", "AT", "AX", "ID", "TO", "TI"]
        print(max_layer(pool, pool))


if __name__ == "__main__":
    unittest.main()   