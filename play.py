import sys
from collections import defaultdict
from numpy import mean
from random import choice, sample, shuffle
from tqdm import tqdm
from util import read_words
from constraints import get_constraints, is_permitted, get_constraint_colors
from infomax import expectation
from agent import WordleAgent
import pygame as pg
from graphics import CartesianPlane, WordleLetter, WordleSlot, PlayButton, Histogram


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


class WordlePlayer:

    def __init__(self, agent, allowed_guesses, pool):
        self.agent = agent
        self.allowed_guesses = allowed_guesses
        self.pool = pool
        self.results = []
        self.target_queue = [word for word in self.pool]
        shuffle(self.target_queue)
        self.busy = False

    def most_recent_result(self):
        if len(self.results) > 0:
            return self.results[-1]
        else:
            return None

    def play_one(self, target=None):
        if target is None:
            target = choice(self.pool)
        game_over = False
        round = 0
        guess = self.agent.first_guess()
        guesses = [guess]
        pool = [word for word in self.pool]
        while not game_over:
            round += 1
            if guess == target or round > 6:
                game_over = True
            else:
                pool = update_pool(guess, target, pool)
                guess = self.agent.make_guess(self.allowed_guesses, pool)
                guesses.append(guess)
        return guesses

    def notify(self, event):
        pass

    def draw(self, screen):
        self.update()

    def update(self):
        if not self.busy and len(self.target_queue) > 0:
            target, self.target_queue = self.target_queue[0], self.target_queue[1:]
            self.busy = True
            guesses = self.play_one(target)
            self.results.append((target, guesses))
            self.busy = False
            return len(guesses)

class WordleGame:

    def __init__(self, agent, allowed_guesses, pool):
        pg.init()
        if not pg.font:
            print("Warning, fonts disabled")
        if not pg.mixer:
            print("Warning, sound disabled")
        pg.display.set_caption("Wordle")
        pg.mouse.set_visible(True)
        self.clock = pg.time.Clock()
        self.clock.tick(60)
        self.y_max = 7
        self.plane = CartesianPlane(x_max=8, y_max=self.y_max, screen_width=440, screen_height=385)
        self.round = 0
        for y in range(self.y_max-6, self.y_max):
            for x in range(1, 6):
                self.plane.add_sprite(WordleSlot(x,y))
        self.player = WordlePlayer(agent, allowed_guesses, pool)
        self.histogram = Histogram(x=330, y=305)
        self.plane.add_widget(self.histogram)
        self.target = None
        self.guess_queue = []

    def refresh(self):
        self.round = 0
        self.target, self.guess_queue = self.player.most_recent_result()
        self.plane.clear()
        for y in range(self.y_max-6, self.y_max):
            for x in range(1, 6):
                self.plane.add_sprite(WordleSlot(x,y))
        self.plane.add_widget(self.histogram)

    def guess_word(self, word):
        colors = get_constraint_colors(guess=word, target=self.target)
        letters = [WordleLetter(word[0], colors[0], 1, self.y_max-self.round),
                   WordleLetter(word[1], colors[1], 2, self.y_max-self.round),
                   WordleLetter(word[2], colors[2], 3, self.y_max-self.round),
                   WordleLetter(word[3], colors[3], 4, self.y_max-self.round),
                   WordleLetter(word[4], colors[4], 5, self.y_max-self.round)]
        for i, letter in enumerate(letters):
            self.plane.add_sprite(letter)
            letter.appear(delay=i*6)
            if word == self.target:
               letter.dance(delay=40+i*6)
        return letters

    def loop(self):
        end_game = False
        game_over = False
        active_letters = []
        for _ in range(15):
            num_guesses = self.player.update()
            self.histogram.report_win(num_guesses)
        while not end_game and not (game_over and len(active_letters) == 0):
            for event in pg.event.get():
                self.plane.notify(event)
                if event.type == pg.QUIT:
                    game_over = True
                    end_game = True
            if len(active_letters) == 0 and len(self.guess_queue) == 0:
                game_over = True
            elif len(active_letters) == 0:
                self.round += 1
                guess, self.guess_queue = self.guess_queue[0], self.guess_queue[1:]
                active_letters = self.guess_word(guess)
                num_guesses = self.player.update()
                self.histogram.report_win(num_guesses)
                if guess == self.target or self.round > 6:
                    game_over = True
            active_letters = [letter for letter in active_letters if letter.active()]
            self.plane.refresh()
        return end_game




class WordleGame2:

    def __init__(self, agent, allowed_guesses, pool, target=None):
        pg.init()
        if not pg.font:
            print("Warning, fonts disabled")
        if not pg.mixer:
            print("Warning, sound disabled")
        pg.display.set_caption("Wordle")
        pg.mouse.set_visible(True)
        self.plane = CartesianPlane(x_max=6, y_max=8, screen_width=330, screen_height=440)
        self.plane.add_sprite(PlayButton(3,0.75))
        for y in range(2, 8):
            for x in range(1, 6):
                self.plane.add_sprite(WordleSlot(x,y))
        self.round = 0
        self.agent = agent
        self.allowed_guesses = allowed_guesses
        self.pool = pool
        self.target = target
        if self.target is None:
            self.target = choice(pool)

    def refresh(self):
        self.plane.clear()
        self.plane.add_sprite(PlayButton(3,0.75))
        for y in range(2, 8):
            for x in range(1, 6):
                self.plane.add_sprite(WordleSlot(x,y))
        self.round = 0
        self.target = choice(self.pool)

    def guess_word(self, word):
        colors = get_constraint_colors(guess=word, target=self.target)
        letters = [WordleLetter(word[0], colors[0], 1, 8-self.round),
                   WordleLetter(word[1], colors[1], 2, 8-self.round),
                   WordleLetter(word[2], colors[2], 3, 8-self.round),
                   WordleLetter(word[3], colors[3], 4, 8-self.round),
                   WordleLetter(word[4], colors[4], 5, 8-self.round)]
        for i, letter in enumerate(letters):
            self.plane.add_sprite(letter)
            letter.appear(delay=i*6)
            if word == self.target:
               letter.dance(delay=40+i*6)
        return letters

    def start(self):
        clock = pg.time.Clock()
        end_game = False
        game_over = False
        game_will_be_over = False
        guess = self.agent.first_guess()
        pool = self.pool
        while not game_over:
            clock.tick(60)
            for event in pg.event.get():
                self.plane.notify(event)
                if event.type == pg.QUIT:
                    game_over = True
                    end_game = True
                elif event.type == pg.MOUSEBUTTONDOWN and game_will_be_over:
                    game_over = True
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.round += 1
                    self.guess_word(guess)
                    if guess == self.target:
                        game_will_be_over = True
                    else:
                        pool = update_pool(guess, self.target, pool)
                        if self.round > 6:
                            game_will_be_over = True
                        else:
                            guess = self.agent.make_guess(self.allowed_guesses, pool)
            self.plane.refresh()
        return end_game

    def loop(self):
        clock = pg.time.Clock()
        end_game = False
        game_over = False
        game_will_be_over = False
        guess = self.agent.first_guess()
        pool = self.pool
        iteration = 0
        active_letters = []
        while not end_game and not (game_over and len(active_letters) == 0):
            clock.tick(60)
            iteration += 1
            for event in pg.event.get():
                self.plane.notify(event)
                if event.type == pg.QUIT:
                    game_over = True
                    end_game = True
            if game_will_be_over or game_over:
                game_over = True
            elif len(active_letters) == 0:
                self.round += 1
                active_letters = self.guess_word(guess)
                if guess == self.target:
                    game_will_be_over = True
                else:
                    pool = update_pool(guess, self.target, pool)
                    if self.round > 6:
                        game_will_be_over = True
                    else:
                        guess = self.agent.make_guess(self.allowed_guesses, pool)
            active_letters = [letter for letter in active_letters if letter.active()]
            self.plane.refresh()
        return end_game





if __name__ == "__main__":
    if len(sys.argv) == 4:
        play_many(WordleAgent(expectation), read_words(sys.argv[1]),
                  read_words(sys.argv[2]), int(sys.argv[3]))
    else:
        game = WordleGame(WordleAgent(expectation, track_progress=False),
                          read_words(sys.argv[1]), read_words(sys.argv[2]))
        going = True
        while going:
            if game.loop():
                pg.quit()
                going = False
            else:
                game.refresh()