import sys
from abc import ABC, abstractmethod
from numpy import mean
from random import sample
from util import read_words
from constraints import get_constraints, is_permitted


def reduction(guess, target, pool):
    """Computes the percentage of the word pool that remains possible after a guess.

    Parameters
    ----------
    guess : str
        The guessed word
    target : str
        The game's secret target word
    pool : iterable[str]
        The pool of possible guesses, prior to the current guess

    Returns
    -------
    float
        The percentage of the pool that remains possible after the guess
    """

    constraints = get_constraints(guess, target)
    permitted = [word for word in pool if is_permitted(word, constraints)]
    return len(permitted) / len(pool)


def expected_reduction(guess, targets, pool):
    return mean([reduction(guess, target, pool) for target in targets])


def best_expected_reduction(targets, pool):
    eps = 0.000001
    best, best_reduction = None, 1.0 + eps
    for guess in pool:
        guess_reduction = expected_reduction(guess, targets, pool)
        if guess_reduction < best_reduction:
            best, best_reduction = guess, guess_reduction
    return best


def montecarlo(num_samples):
    allowed = read_words('wordle-allowed-guesses.txt')
    subset = sample(allowed, num_samples)
    best_guess = best_expected_reduction(subset, subset)
    print(f"From a random pool of {num_samples} words:")
    print(f"  the best first guess is {best_guess}")


def main(wordfile, max_words=None):
    allowed = read_words(wordfile)
    if max_words is not None:
        allowed = allowed[:max_words]
    best_guess = best_expected_reduction(allowed, allowed)
    print(f"From the pool of {len(allowed)} words:")
    print(f"  the best first guess is {best_guess}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))