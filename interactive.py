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


class BaseGame:

    def __init__(self):
        self.clock = BaseGame.initialize_pygame()

    @staticmethod
    def initialize_pygame():
        pg.init()
        if not pg.font:
            print("Warning, fonts disabled")
        if not pg.mixer:
            print("Warning, sound disabled")
        pg.display.set_caption("Wordle")
        pg.mouse.set_visible(True)
        clock = pg.time.Clock()
        clock.tick(60)
        return clock

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


class WordleInteractive(BaseGame):
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
        self.agent = agent
        self.allowed_guesses = allowed_guesses
        self.pool = pool
        self.round = 0
        self.target = None
        self.y_max = 8
        self.plane = CartesianPlane(x_max=6, y_max=8, screen_width=330, screen_height=440)
        self.refresh()

    def refresh(self):
        self.plane.clear()
        self.plane.add_sprite(PlayButton(3,0.75))
        for y in range(2, 8):
            for x in range(1, 6):
                self.plane.add_sprite(WordleSlot(x,y))
        self.round = 0
        self.target = choice(self.pool)

    def play(self):
        end_game = False
        game_over = False
        game_will_be_over = False
        guess = self.agent.first_guess()
        pool = self.pool
        while not game_over:
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


if __name__ == "__main__":
    game = WordleInteractive(WordleAgent(expectation, track_progress=False),
                             read_words(sys.argv[1]), read_words(sys.argv[2]))
    going = True
    while going:
        if game.play():
            pg.quit()
            going = False
        else:
            game.refresh()