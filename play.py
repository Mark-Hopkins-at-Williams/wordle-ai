import sys
from collections import defaultdict
from numpy import mean
from random import choice, sample, shuffle
from tqdm import tqdm
from util import read_words
from constraints import get_constraints, is_permitted
from infomax import expectation
from agent import WordleAgent

def update_pool(guess, target, pool):
    """Updates the pool of possible answers after a guess.

    Parameters
    ----------
    guess : str
        The player's guess
    target : str
        The hidden target word
    pool : list[str]
        Original pool of possible answers.

    Returns
    -------
    list[str]
        The subset of the original pool that remain possible after making the guess.
    """

    constraints = get_constraints(guess, target)
    permitted = [word for word in pool if is_permitted(word, constraints)]
    return permitted


def play(agent, allowed_guesses, pool, target=None, logger=print):
    """Plays a complete game of Wordle.

    Parameters
    ----------
    agent : agent.WordleAgent
        AI who will play Wordle
    allowed_guesses : list[str]
        List of allowable guesses.
    pool : list[str]
        Pool of possible answers.
    target : str
        The hidden target word for this game
    logger : function
        Function for logging game progress.

    Returns
    -------
    int
        The number of rounds it took the agent to win the game
    """

    if target is None:
        target = choice(pool)
    game_over = False
    round = 0
    guess = agent.first_guess()
    while not game_over:
        round += 1
        logger(f"Round {round}!")
        if guess == target:
            game_over = True
            msg = f"  guessed {guess}; CORRECT!"
        else:
            pool = update_pool(guess, target, pool)
            msg = f"  guessed {guess}; reduced pool to {len(pool)} words."
        logger(msg)
        if round > 6:
            game_over = True
        else:
            guess = agent.make_guess(allowed_guesses, pool)
    return round


def play_many(agent, allowed_guesses, pool, k=None, logger=print):
    """Plays a sequence of Wordle games.

    Parameters
    ----------
    agent : agent.WordleAgent
        AI who will play Wordle
    allowed_guesses : list[str]
        List of allowable guesses.
    pool : list[str]
        Pool of possible answers.
    k : int
        The number of games to play. If None, then this function will play one game for
        every word in the pool of possible answers.
    logger : function
        Function for logging game progress.

    Returns
    -------
    float
        The average number of rounds it took the agent to win the game
    """

    results = []
    shuffle(pool)
    if k is None:
        k = len(pool)
    for target in pool[:k]:
        results.append(play(agent, allowed_guesses, pool, target,
                            logger=lambda s: None))
        logger(f"After {len(results)} games, average number of guesses is: {mean(results):.2f}")
    return mean(results)



if __name__ == "__main__":
    if len(sys.argv) == 4:
        play_many(WordleAgent(expectation), read_words(sys.argv[1]),
                  read_words(sys.argv[2]), int(sys.argv[3]))
    else:
        play(WordleAgent(expectation), read_words(sys.argv[1]), read_words(sys.argv[2]))
