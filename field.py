import pygame as pg
import numpy as np


class Field:
    def __init__(self, width, height, color1, color2, color3, color4):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 50
        self.top = 50
        self.cell_size = 50
        self.left_top = color1
        self.right_top = color2
        self.left_bottom = color3
        self.right_bottom = color4
        self.elements = []

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, surface):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                pg.draw.rect(surface, 'white',
                             (self.left + c * self.cell_size,
                              self.top + r * self.cell_size,
                              self.cell_size, self.cell_size))

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


class Element(pg.sprite.Sprite):
    def __init__(self, left, top, cell_size, color, *groups):
        super(Element, self).__init__(*groups)
        # self.rect = left, top, cell_size, color

    def update(self, frames, speed) -> None:
        pass


all_sprites = pg.sprite.Group()
for r in range(8):
    for c in range(8):
        Element(75, 'red', all_sprites)

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((500, 650))
    game = Field(6, 8, (22, 235, 86), (225, 255, 55), (54, 39, 152), (220, 87, 82))
    game.set_view(25, 25, 75)
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 0, 0))
        game.render(screen)
        all_sprites.draw(screen)
        pg.display.flip()
    pg.quit()
