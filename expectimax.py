import sys
from collections import defaultdict
from numpy import mean
from random import choice, sample, shuffle
from tqdm import tqdm
from util import read_words
from constraints import get_constraints, is_permitted
from infomax import split_pool


def max_layer(allowed_guesses, answer_pool):
    best_guess, best_value = None, float('inf')
    for guess in allowed_guesses:
        revised_guesses = [g for g in allowed_guesses if g != guess]
        if guess in answer_pool:
            revised_pool = [answer for answer in answer_pool if answer != guess]
            value = ((1 + (1 + expectation_layer(guess, revised_pool, revised_guesses)) * len(revised_pool)) /
                     (1 + len(revised_pool)))
        else:
            value = 1 + expectation_layer(guess, answer_pool, revised_guesses)
        if value < best_value:
            best_guess, best_value = guess, value
    return best_guess, best_value


def expectation_layer(guess, pool, allowed_guesses, position=0):
    partitions = split_pool(pool, guess[position], position)
    result = 0
    for partition in partitions:
        if len(partition) > 0:
            factor = len(partition) / len(pool)
            if position + 1 >= len(guess):
                _, expected_size = max_layer(allowed_guesses, partition)
            else:
                expected_size = expectation_layer(guess, partition, allowed_guesses, position + 1)
            result += factor * expected_size
    return result


if __name__ == "__main__":
    allowed_file = sys.argv[1]
    answer_file = sys.argv[2]
    print(max_layer(read_words(allowed_file), read_words(answer_file)))

