import sys
from collections import defaultdict
from numpy import mean
from random import choice, sample, shuffle
from tqdm import tqdm
from util import read_words
from constraints import update_pool, get_constraint_colors
from infomax import expectation
from agent import WordleAgent
import pygame as pg
from graphics import CartesianPlane, WordleLetter, WordleSlot, PlayButton, Histogram
from interactive import BaseGame


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

    def play_one(self, target):
        guess = self.agent.first_guess()
        guesses = [guess]
        pool = [word for word in self.pool]
        game_over = False
        while not game_over:
            if guess == target or len(guesses) == 6:
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


class WordleFlow(BaseGame):
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
    """

    def __init__(self, agent, allowed_guesses, pool):
        super().__init__()
        self.round = 0
        self.y_max = 7
        self.plane = CartesianPlane(x_max=8, y_max=self.y_max,
                                    screen_width=440, screen_height=385)
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

    def play(self):
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


if __name__ == "__main__":
    game = WordleFlow(WordleAgent(expectation, track_progress=False),
                      read_words(sys.argv[1]), read_words(sys.argv[2]))
    going = True
    while going:
        if game.play():
            pg.quit()
            going = False
        else:
            game.refresh()