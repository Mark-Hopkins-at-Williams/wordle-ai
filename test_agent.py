##
# test_agent.py
# Unit tests for agent.py.
##


import unittest
from infomax import expectation
from agent import WordleAgent

class TestAgent(unittest.TestCase):

    def test_score_guesses(self):
        agent = WordleAgent(cost_fn=expectation)
        pool = ["AD", "AT", "AX", "ID", "TO", "TI"]
        scored_guesses = agent.score_guesses(["AT", "AX", "ID", "TI"], pool)
        costs = [cost for cost, _ in scored_guesses]
        ranked = [guess for _, guess in scored_guesses]
        self.assertEqual(ranked, ["TI", "AT", "ID", "AX"])
        self.assertAlmostEqual(costs[0], 4/3)
        self.assertAlmostEqual(costs[1], 5/3)
        self.assertAlmostEqual(costs[2], 2)
        self.assertAlmostEqual(costs[3], 7/3)

    def test_lowest_cost_guess(self):
        agent = WordleAgent(cost_fn=expectation)
        pool = ["AD", "AT", "AX", "ID", "TO", "TI"]
        guess = agent.lowest_cost_guess(["AT", "AX", "ID", "TI"], pool)
        self.assertEqual(guess, "TI")
        guess = agent.lowest_cost_guess(["AT", "AX", "ID", "TO"], pool)
        self.assertEqual(guess, "AT")


if __name__ == "__main__":
    unittest.main()   