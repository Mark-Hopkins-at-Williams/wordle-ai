import numpy as np
import os
import pygame as pg


def load_image(filename, scale=None, colorkey=-1):
    image = pg.image.load(filename)
    image = image.convert()
    size = image.get_size()
    if scale is not None:
        size = (size[0] * scale[0], size[1] * scale[1])
        image = pg.transform.scale(image, size)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()


class CartesianPlane:
    def __init__(self, x_max, y_max, screen_width, screen_height,
                 bg_color=(255, 255, 255)):
        self.screen = pg.display.set_mode((screen_width, screen_height))
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(bg_color)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.x_max = x_max
        self.y_max = y_max
        self.x_pixel_increment = self.screen_width // self.x_max
        self.y_pixel_increment = self.screen_height // self.y_max
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()
        self.sprite_list = []
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)
        self.widgets = []

    def clear(self):
        self.sprite_list = []
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)
        self.widgets = []

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)

    def add_widget(self, widget):
        self.widgets.append(widget)

    def refresh(self):
        self.screen.blit(self.background, (0, 0))
        self.sprites.update()
        for sprite in self.sprites:
            sprite.redraw()
            x, y = sprite.current_position()
            coords = self.translate_coordinates(x, y)
            if coords is not None:
                width, height = sprite.size()
                sprite.rect = coords[0] - width//2, coords[1] - height//2
        self.sprites.draw(self.screen)
        for widget in self.widgets:
            widget.draw(self.screen)
        pg.display.flip()

    def notify(self, event):
        for sprite in self.sprites:
            sprite.notify(event)
        for widget in self.widgets:
            widget.notify(event)

    def in_bounds(self, x, y):
        return 0 <= x <= self.x_max, 0 <= y <= self.y_max

    def translate_coordinates(self, x, y):
        return (x * self.x_pixel_increment,
                self.screen_height - (y * self.y_pixel_increment))


class WordleLetter(pg.sprite.Sprite):

    def __init__(self, letter, color, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.cell_scale = (1.0, 1.0)
        self.image_file = f"images/{color}.{letter}.png"
        self.image, self.rect = load_image(self.image_file, scale=self.cell_scale, colorkey=0)
        self.y_scale_queue = [1.0]
        self.y_pos_queue = []

    def size(self):
        return self.rect.width, self.rect.height

    def current_position(self):
        return self.x, self.y

    def move(self, delta_x, delta_y):
        step_size = (delta_x / self.move_divisor, delta_y / self.move_divisor)
        self.move_queue += [step_size] * self.move_divisor

    def notify(self, event):
        pass

    def active(self):
        return len(self.y_scale_queue) > 0 or len(self.y_pos_queue) > 0

    def appear(self, delay=0):
        self.y_scale_queue = [0] * delay
        self.y_scale_queue += list([0.05 * i for i in range(1, 21)])

    def dance(self, delay=0):
        self.y_pos_queue = [self.y] * delay
        self.y_pos_queue += list([self.y + .04*i for i in range(1, 11)])
        self.y_pos_queue += list([self.y + .04*i for i in range(10, -1, -1)])

    def redraw(self):
        self.image, self.rect = load_image(self.image_file, scale=self.cell_scale, colorkey=0)

    def update(self):
        if len(self.y_scale_queue) > 0:
            y_scale, self.y_scale_queue = self.y_scale_queue[0], self.y_scale_queue[1:]
            self.cell_scale = (self.cell_scale[0], y_scale)
        if len(self.y_pos_queue) > 0:
            self.y, self.y_pos_queue = self.y_pos_queue[0], self.y_pos_queue[1:]
        self.redraw()


class WordleSlot(pg.sprite.Sprite):

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.cell_scale = (1.0, 1.0)
        self.image_file = f"images/slot.png"
        self.image, self.rect = load_image(self.image_file, scale=self.cell_scale, colorkey=0)

    def size(self):
        return self.rect.width, self.rect.height

    def current_position(self):
        return self.x, self.y

    def notify(self, event):
        pass

    def redraw(self):
        self.image, self.rect = load_image(self.image_file, scale=self.cell_scale, colorkey=0)

    def update(self):
        self.redraw()


class Histogram:

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.wins = [0, 0, 0, 0, 0, 0]

    def report_win(self, guess_count):
        if 1 <= guess_count <= len(self.wins):
            self.wins[guess_count-1] += 1

    def draw(self, screen):
        pg.draw.rect(screen, "gray", (self.x, self.y, 90, 1))
        color = (121, 168, 107)
        for guess_count, num_wins in enumerate(self.wins):
            myfont = pg.font.SysFont("monospace", 15)
            text = myfont.render(str(guess_count+1), 1, "black")
            screen.blit(text, (self.x + 15 * guess_count, self.y + 10))
            pg.draw.rect(screen, color, (self.x + 15 * guess_count,
                                         self.y - self.wins[guess_count],
                                         10, self.wins[guess_count]))
        average = sum([(i+1)*count for i, count in enumerate(self.wins)]) / sum(self.wins)
        average = f"{average:.2f}"
        myfont = pg.font.SysFont("monospace", 25)
        text = myfont.render(average, 1, (61, 108, 47))
        screen.blit(text, (self.x + 13, self.y + 30))

    def notify(self, event):
        pass


class PlayButton(pg.sprite.Sprite):

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.cell_scale = (1, 1)
        self.image_file = f"images/play.png"
        self.image, self.rect = load_image(self.image_file, colorkey=0)

    def size(self):
        return self.rect.width, self.rect.height

    def current_position(self):
        return self.x, self.y

    def notify(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.image_file = f"images/play_pushed.png"
        elif event.type == pg.MOUSEBUTTONUP:
            self.image_file = f"images/play.png"

    def redraw(self):
        self.image, self.rect = load_image(self.image_file, colorkey=0)

    def update(self):
        self.redraw()