import sys
from abc import ABC, abstractmethod
from numpy import mean
from random import sample
from util import read_words


class Constraint(ABC):

    @abstractmethod
    def permits(self, word):
        ...

class EqualityConstraint(Constraint):

    def __init__(self, letter, position):
        self.letter = letter
        self.position = position

    def permits(self, word):
        return word[self.position] == self.letter

    def __eq__(self, other):
        return self.letter == other.letter and self.position == other.position

    def __hash__(self):
        return hash(self.letter) + hash(self.position)

    def __str__(self):
        return f"{self.letter} at {self.position}"

    __repr__ = __str__


class MembershipConstraint(Constraint):
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


def get_constraint(letter, pos, target):
    if target[pos] == letter:
        return EqualityConstraint(letter, pos)
    elif letter in target:
        return MembershipConstraint(letter, set(range(len(target))) - {pos})
    else:
        return MembershipConstraint(letter, set([]))


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
        result.append(get_constraint(letter, pos, target))
    return set(result)

