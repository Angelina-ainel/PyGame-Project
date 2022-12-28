import pygame as pg
import numpy as np
from PIL import ImageColor
import random

fixed_elems = ['4 corners', 'whole frame', 'vertical lines', 'horizontal lines']


def condition(elem):
    if not elem.mixed and not elem.fixed:
        return True
    return False


class Element(pg.sprite.Sprite):
    def __init__(self, row, col, top, cell_size, color, fixed, id, *groups):
        super(Element, self).__init__(*groups)
        self.image = pg.Surface((cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.color = color
        pg.draw.rect(self.image, self.color, self.rect)
        self.fixed = fixed
        if self.fixed:
            pg.draw.circle(self.image, 'black', self.rect.center, cell_size // 17)
        self.mixed = False
        self.rect.x = col * cell_size
        self.rect.y = top + row * cell_size
        self.id = id
        self.pushed = False
        self.size = cell_size
        self.group = groups[0]

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and args[0].button == pg.BUTTON_LEFT:
            if self.rect.x < event.pos[0] < self.rect.x + self.size and \
                    self.rect.y < event.pos[1] < self.rect.y + self.size and not self.fixed:
                self.pushed = True
        if args and args[0].type == pg.MOUSEBUTTONUP:
            if self.pushed:
                if pg.sprite.spritecollide(self, self.group, False):
                    # print(pg.sprite.spritecollide(self, self.group, False))
                    pass
            self.pushed = False

        if args and args[0].type == pg.MOUSEMOTION:
            if self.pushed:
                dx, dy = args[0].rel
                self.rect.topleft = self.rect.x + dx, self.rect.y + dy


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
            if c < self.width:
                if c == 0 and r != 0:
                    c += 1
                fixing = self.check_fixing(r, c)
                color = self.left_top + (coeff_h_left * r) + (coeff_w * c)
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

    def mix_elements(self):
        for i in range(len(self.list_elems)):
            if not self.list_elems[i].mixed and not self.list_elems[i].fixed:
                pair = random.choice(list(filter(condition, self.list_elems)))
                self.list_elems[i].rect.topleft, pair.rect.topleft = pair.rect.topleft, self.list_elems[i].rect.topleft
                pair.mixed = True
                self.list_elems[i].mixed = True

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
    screen = pg.display.set_mode((450, 750))
    lt = np.array((31, 255, 255))
    rt = np.array((90, 255, 106))
    lb = np.array((255, 118, 233))
    rb = np.array((255, 250, 63))

    level = Field(6, 8, lt, rt, lb, rb, '4 corners')
    level.set_view(0, 75, 75)
    running = True
    pushed = False
    level.render()
    level.mix_elements()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            level.all_elems.update(event)
        screen.fill((0, 0, 0))
        level.all_elems.draw(screen)

        pg.display.flip()
    pg.quit()
