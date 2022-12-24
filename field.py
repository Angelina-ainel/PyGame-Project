import pygame as pg
import numpy as np
from PIL import ImageColor
import random

fixed_elems = ['4 corners', 'whole frame', 'vertical lines', 'horizontal lines']


class Element(pg.sprite.Sprite):
    def __init__(self, row, col, top, cell_size, color, fixed, id, *groups):
        super(Element, self).__init__(*groups)
        self.image = pg.Surface((cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.color = color
        pg.draw.rect(self.image, self.color, self.rect)
        self.rect.x = col * cell_size
        self.rect.y = top + row * cell_size
        self.id = id
        self.fixed = fixed
        if self.fixed:
            pg.draw.circle(self.image, 'black', self.rect.center, 10)
        self.mixed = False

    def update(self):
        pass


class Field:
    def __init__(self, width, height, color1, color2, color3, color4, type):
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
        self.mixed_elems = pg.sprite.Group()
        self.list_elems = []
        self.fixed_elems = type
        self.mixed = False

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def check_fixing(self, r, c):
        if self.fixed_elems == '4 corners':
            if (c == 0 and r == 0) or (c == 0 and r == self.height - 1) \
                    or (c == self.width - 1 and r == 0) or (c == self.width - 1 and r == self.height - 1):
                return True
            return False

    def render(self):
        id = 1
        r, c = 0, 0
        coeff_h_left = np.trunc((self.left_bottom - self.left_top) / (self.height - 1))
        coeff_h_right = np.trunc((self.right_bottom - self.right_top) / (self.height - 1))
        for n in range(self.height * self.width):
            coeff_w = np.trunc(((self.right_top + (coeff_h_right * r)) -
                       (self.left_top + (coeff_h_left * r))) / (self.width - 1))
            # print(r, c)
            if c < self.width:
                if c == 0 and r != 0:
                    c += 1
                fixing = self.check_fixing(r, c)
                color = self.left_top + (coeff_h_left * r) + (coeff_w * c)
                # print(color)
                sprite = Element(r, c, self.top, self.cell_size, color, fixing, id, self.all_elems)
                c += 1
                id += 1
                self.list_elems.append(sprite)
            else:
                c = 0
                r += 1
                fixing = self.check_fixing(r, c)
                sprite = Element(r, c, self.top, self.cell_size,
                                 self.left_top + (coeff_h_left * r), fixing, id, self.all_elems)
                id += 1
                self.list_elems.append(sprite)
        # self.mix_elements()

    def mix_elements(self):
        # можно сделать так и вставять нефиксированные плитки на опр. позицию insert'ом
        # np_elems = np.array(self.list_elems)
        # not_fixed_tiles = list(filter(lambda el: not el.fixed, self.list_elems))
        for i in range(len(self.list_elems)):
            if not self.list_elems[i].mixed and not self.list_elems[i].fixed:
                filtered = [tile for tile in self.list_elems if
                            not tile.mixed and not tile.fixed and tile != self.list_elems[i]]
                for el in filtered:
                    print(el.id, end='; ')
                # для фильтра написать отдельную функцию
                # for el in list(filter(lambda tile: not tile.fixed and tile != self.list_elems[i], self.list_elems)):
                    # print(el.id, end='; ')
                pair = random.choice([tile for tile in self.list_elems if
                                      not tile.mixed and not tile.fixed and tile != self.list_elems[i]])
                print(self.list_elems[i].id, pair.id)
                self.list_elems[i] = pair
                self.list_elems[self.list_elems.index(pair)] = self.list_elems[i]
                pair.mixed = True
                self.list_elems[i].mixed = True
        self.mixed_elems.add(*self.list_elems)
        for el in self.list_elems:
            print(el.id, end=', ')
        # проверить это и отрисовать

    def make_array(self):
        np_colors = np.array(self.list_elems)
        for el in self.list_elems:
            print(el.fixed)

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
    lt = np.array((234, 31, 255))
    rt = np.array((255, 234, 31))
    lb = np.array((220, 210, 255))
    rb = np.array((30, 2, 140))

    level = Field(6, 8, lt, rt, lb, rb, '4 corners')
    level.set_view(0, 75, 50)
    running = True
    level.render()
    level.mix_elements()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 0, 0))
        # level.mixed_elems.draw(screen)
        level.all_elems.draw(screen)

        pg.display.flip()
    pg.quit()
