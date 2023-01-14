import pygame as pg
import numpy as np
from PIL import ImageColor
import random
import sqlite3


def condition_to_mix(elem):
    if not elem.mixed and not elem.fixed:
        return True
    return False


class Element(pg.sprite.Sprite):
    def __init__(self, row, col, top, cell_size, color, fixed, id, *groups):
        super(Element, self).__init__(*groups)
        self.width = cell_size[0]
        self.height = cell_size[1]
        self.size = cell_size
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.color = color
        pg.draw.rect(self.image, self.color, self.rect)
        self.fixed = fixed
        if self.fixed:
            pg.draw.circle(self.image, 'black', self.rect.center, self.width // 20)
        self.mixed = False
        self.rect.x = col * self.width
        self.rect.y = top + row * self.height
        self.id = id
        self.pushed = False
        self.group1 = groups[0]

        self.pushed_elem_topleft = 0, 0

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and args[0].button == pg.BUTTON_LEFT:
            if self.rect.x < args[0].pos[0] < self.rect.x + self.width and \
                    self.rect.y < args[0].pos[1] < self.rect.y + self.height and not self.fixed:
                self.pushed = True
                self.pushed_elem_topleft = self.rect.topleft
                self.group1.remove(self)
                self.group1.add(self)
        if args and args[0].type == pg.MOUSEBUTTONUP:
            if self.pushed:
                colisions = list(filter(lambda sprite: pg.sprite.collide_mask(self, sprite) and not sprite.fixed
                                         and sprite != self, self.group1))
                if colisions:
                    change_places = max(colisions,
                                        key=lambda s: self.mask.overlap_area(s.mask, (self.rect.x - s.rect.x,
                                                                                      self.rect.y - s.rect.y)))
                    if self.rect.width * self.rect.height // 2 < \
                            self.mask.overlap_area(change_places.mask,
                                                   (
                                                           self.rect.x - change_places.rect.x,
                                                           self.rect.y - change_places.rect.y)):
                        self.rect.topleft, change_places.rect.topleft = change_places.rect.topleft, \
                                                                        self.pushed_elem_topleft
                        self.id, change_places.id = change_places.id, self.id
                    else:
                        self.rect.topleft = self.pushed_elem_topleft
                else:
                    self.rect.topleft = self.pushed_elem_topleft
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
        self.sprite_group1 = pg.sprite.Group()
        self.sprite_group2 = pg.sprite.Group()
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
        elif self.fixed_elems == 'vertical lines':
            if c == 0 or c == self.width - 1:
                return True
        elif self.fixed_elems == 'horizontal lines':
            if r == 0 or r == self.height - 1:
                return True
        elif self.fixed_elems == 'frame':
            if c == 0 or c == self.width - 1 or r == 0 or r == self.height - 1:
                return True
        elif self.fixed_elems == 'chess':
            if (c % 2 == 0 and r % 2 == 0) or (c % 2 and r % 2):
                return True
        elif self.fixed_elems == 'through_one':
            if c % 2 == 0 and r % 2 == 0:
                return True
        elif self.fixed_elems == 'only_one':
            if c == 0 and r == self.height - 1:
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
                Element(r, c, self.top, self.cell_size, color, fixing, id, self.sprite_group1,
                        self.sprite_group2)
                c += 1
                id += 1
            else:
                c = 0
                r += 1
                fixing = self.check_fixing(r, c)
                Element(r, c, self.top, self.cell_size,
                        self.left_top + (coeff_h_left * r), fixing, id, self.sprite_group1, self.sprite_group2)
                id += 1

    def mix_elements(self):
        sprites_list = self.sprite_group1.sprites()
        for i in range(len(sprites_list)):
            if not sprites_list[i].mixed and not sprites_list[i].fixed:
                pair = random.choice(list(filter(condition_to_mix, sprites_list)))
                sprites_list[i].rect, pair.rect = pair.rect, sprites_list[i].rect
                sprites_list[i].id, pair.id = pair.id, sprites_list[i].id
                pair.mixed = True
                sprites_list[i].mixed = True


pg.init()
width, height = size = 500, 700
screen = pg.display.set_mode(size)
con = sqlite3.connect("color_schemes.db")
query = """SELECT levels.left_top, levels.right_top, levels.left_bottom, levels.right_bottom, levels.size,
templates.type, difficulties.difficulty
FROM levels INNER JOIN templates ON templates.id = levels.template
INNER JOIN difficulties ON difficulties.id = levels.difficulty
"""
result = con.cursor().execute(query).fetchall()
# print(result)
field1 = result[0]
size = list(map(int, field1[4].split('*')))
print(size)
lt = np.array(ImageColor.getcolor(field1[0], "RGB"))
rt = np.array(ImageColor.getcolor(field1[1], "RGB"))
lb = np.array(ImageColor.getcolor(field1[2], "RGB"))
rb = np.array(ImageColor.getcolor(field1[3], "RGB"))
level = Field(3, 3, lt, rt, lb, rb, field1[5])
level.set_view(0, 0, (100, 100))
level.render()
screen.fill((0, 0, 0))
level.sprite_group1.draw(screen)
pg.display.flip()
image = pg.transform.scale(screen, (150, 150))
pg.image.save(screen, 'data/beginner_1.jpg')
