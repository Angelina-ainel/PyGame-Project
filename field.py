import pygame as pg
import numpy as np
from PIL import ImageColor
import random


class Element(pg.sprite.Sprite):
    def __init__(self, row, col, top, cell_size, color, *groups):
        super(Element, self).__init__(*groups)
        self.image = pg.Surface((cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.color = color
        pg.draw.rect(self.image, self.color, self.rect)
        self.rect.x = col * cell_size
        self.rect.y = top + row * cell_size

    def update(self) -> None:
        pass


class Field:
    def __init__(self, width, height, color1, color2, color3, color4):
        self.width = width
        self.height = height
        self.left = 0
        self.top = 75
        self.cell_size = 75
        self.left_top = color1
        self.right_top = color2
        self.left_bottom = color3
        self.right_bottom = color4
        self.all_elems = pg.sprite.Group()

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        r, c = 0, 0
        coeff_h_left = (self.left_bottom - self.left_top) // self.height
        coeff_h_right = (self.right_bottom - self.right_top) // self.height
        for n in range(self.height * self.width + self.width):
            coeff_w = ((self.right_top + (coeff_h_right * r)) - (self.left_top + (coeff_h_left * r))) // self.width
            if c < self.width:
                if c == 0 and r != 0:
                    c += 1
                Element(r, c, self.top, self.cell_size,
                        self.left_top + (coeff_h_left * r) + (coeff_w * c), self.all_elems)
                c += 1
            else:
                c = 0
                r += 1
                Element(r, c, self.top, self.cell_size, self.left_top + (coeff_h_left * r), self.all_elems)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_coord):
        x, y = mouse_coord
        r, c = (y - self.top) // self.cell_size, (x - self.left) // self.cell_size
        if 0 <= r < self.height and 0 <= c < self.width:
            return r, c
        return None

    def on_click(self, cell):
        print(cell)


if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((950, 950))
    lt = np.array((241, 180, 200))
    rt = np.array((16, 117, 249))
    lb = np.array((130, 210, 120))
    rb = np.array((200, 11, 255))

    level = Field(9, 13, lt, rt, lb, rb)
    level.set_view(0, 75, 50)
    running = True
    level.render()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 0, 0))

        level.all_elems.draw(screen)
        pg.display.flip()
    pg.quit()
