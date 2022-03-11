import sys
from collections import defaultdict
from numpy import mean
from random import choice, sample, shuffle
from tqdm import tqdm
from util import read_words
from constraints import get_constraints, is_permitted
from infomax import expectation


class WordleAgent:

    def __init__(self, cost_fn):
        """
        Parameters
        ----------
        cost_fn : function
            A function that takes a candidate guess and an answer pool as input, and outputs a
            "cost" for the candidate guess. Lower costs should correspond to "better" guesses.
        """

        self.cost_fn = cost_fn

    def score_guesses(self, guesses, pool):
        """Scores each candidate guess, given a pool of possible answers.

        Parameters
        ----------
        guesses : list[str]
            A list of guesses to evaluate
        pool : list[str]
            The current pool of possible answers

        Returns
        -------
        list[tuple]
            A list of (cost, guess) pairs, sorted in increasing order
        """

        word_scores = []
        for word in tqdm(guesses):
            score = self.cost_fn(word, pool)
            word_scores.append((score, word))
        word_scores = sorted(word_scores)
        return word_scores

    def first_guess(self):
        return "raise"

    def make_guess(self, allowed_guesses, pool):
        if len(pool) == 1:
            guess = pool[0]
        elif len(pool) < 4:
            guess = self.lowest_cost_guess(pool, pool)
        else:
            guess = self.lowest_cost_guess(allowed_guesses, pool)
        return guess


    def lowest_cost_guess(self, candidate_guesses, pool):
        """Guesses the candidate with the lowest cost.

        Parameters
        ----------
        candidate_guesses : list[str]
            List of allowed guesses
        pool : list[str]
            Pool of possible answers

        Returns
        -------
        str
            The candidate guess of lowest cost
        """

        word_scores = self.score_guesses(candidate_guesses, pool)
        _, best_word = word_scores[0]
        return best_word


if __name__ == "__main__":
    allowed_file = sys.argv[1]
    answer_file = sys.argv[2]
    agent = WordleAgent(expectation)
    best_guess = agent.make_guess(read_words(allowed_file), read_words(answer_file))
    print(f"The best first guess in Wordle is {best_guess}.")





