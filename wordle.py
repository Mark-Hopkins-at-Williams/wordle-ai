import sys
from numpy import mean
from random import sample

def read_words(filename):
    """Reads a list of words from a file."""

    with open(filename) as reader:
        words = [line.strip() for line in reader]
    return set(words)


class Constraint:
    """Represents a Wordle constraint."""

    def __init__(self, letter, positions):
        """
        Parameters
        ----------
        letter : str
            An alphabetic letter
        positions : set[int]
            Set of permitted word positions where the letter may appear
        """

        self.letter = letter
        self.positions = positions

    def permits(self, word):
        """Returns whether the word is permitted by this constraint.

        Parameters
        ----------
        word : str
            the word to evaluate

        Returns
        -------
        bool
            True iff the input word is consistent with the constraint
        """

        if self.letter not in word and len(self.positions) > 0:
            return False
        for pos, letter in enumerate(word):
            if letter == self.letter and pos not in self.positions:
                return False
        return True

    def __eq__(self, other):
        return self.letter == other.letter and self.positions == other.positions

    def __hash__(self):
        return hash(self.letter) + hash(tuple(self.positions))

    def __str__(self):
        return f"{self.letter} in {self.positions}"

    __repr__ = __str__


def is_permitted(word, constraints):
    """Determines whether a word is consistent with a set of constraints.

    Parameters
    ----------
    word : str
        the word to evaluate
    constraints : iterable[Constraint]
        the set of constraints to consider

    Returns
    -------
    bool
        True iff the input word is consistent with all of the constraints.
    """

    for constraint in constraints:
        if not constraint.permits(word):
            return False
    return True


def get_constraints(guess, target):
    """Produces the set of constraints resulting from a particular guess, given a target.

    Parameters
    ----------
    guess : str
        The guessed word
    target : str
        The game's secret target word

    Returns
    -------
    set[Constraint]
        The set of constraints that result from the player's guess
    """

    result = []
    for pos, letter in enumerate(guess):
        if target[pos] == letter:
            result.append(Constraint(letter, {pos}))
        elif letter in target:
            result.append(Constraint(letter, set(range(len(target))) - {pos}))
        else:
            result.append(Constraint(letter, set([])))
    return set(result)


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


def main(num_samples):
    allowed = read_words('wordle-allowed-guesses.txt')
    subset = sample(allowed, num_samples)
    best_guess = best_expected_reduction(subset, subset)
    print(f"From a random pool of {num_samples} words:")
    print(f"  the best first guess is {best_guess}")


if __name__ == "__main__":
    main(num_samples=int(sys.argv[1]))