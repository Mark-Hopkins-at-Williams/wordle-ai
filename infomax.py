import sys
from collections import defaultdict
from numpy import mean
from random import choice, sample, shuffle
from tqdm import tqdm
from util import read_words
from constraints import get_constraints, is_permitted


def split_pool(pool, letter, position):
    """Splits a pool of words based on feedback from a particular letter-position guess.

    Parameters
    ----------
    pool : list[str]
        The pool of words
    letter : str
        A single letter
    position : int
        A position in a word (counting from zero)

    Returns
    -------
    list[str], list[str], list[str]
        The (green, yellow, gray) partition of the words in the pool according to the
        feedback. Each cell of the partition contains the pool words that are still
        possible, given (green, yellow, gray) feedback from the proposed guess.
    """

    green, yellow, gray = [], [], []
    for word in pool:
        if word[position] == letter:
            green.append(word)
        elif letter in word:
            yellow.append(word)
        else:
            gray.append(word)
    return green, yellow, gray


def expectation(guess, initial_pool):
    """Computes the expected pool size that results from a particular guess.

    Parameters
    ----------
    guess : str
        A candidate word to guess
    initial_pool : list[str]
        The current pool of possible answers
    """

    def expectation_recursive(pool, position):
        partitions = split_pool(pool, guess[position], position)
        result = 0
        for partition in partitions:
            if len(partition) > 0:
                factor = len(partition) / len(pool)
                expected_size = (len(partition) if position + 1 >= len(guess)
                                 else expectation_recursive(partition, position + 1))
                result += factor * expected_size
        return result
    return expectation_recursive(initial_pool, position=0)

