import pygame as pg
import numpy as np
from PIL import ImageColor
import random
import os
import sys


def condition_to_mix(elem):
    if not elem.mixed and not elem.fixed:
        return True
    return False


pg.init()
width, height = size = 490, 720
screen = pg.display.set_mode(size)
count_moves = 0


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
                        global count_moves
                        count_moves += 1
                    else:
                        self.rect.topleft = self.pushed_elem_topleft
                else:
                    self.rect.topleft = self.pushed_elem_topleft
                self.pushed = False

        if args and args[0].type == pg.MOUSEMOTION:
            if self.pushed:
                dx, dy = args[0].rel
                self.rect.topleft = self.rect.x + dx, self.rect.y + dy

    def get_moves(self):
        global count_moves
        return count_moves


class Field:
    def __init__(self, width, height, color1, color2, color3, color4, type):
        self.width = width
        self.height = height
        self.left = 0
        self.top = 0
        self.cell_size = 55, 60
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
                Element(r, c, self.top, self.cell_size, color, fixing, id, self.sprite_group1, self.sprite_group2)
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


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Particle(pg.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (15, 20, 25):
        fire.append(pg.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy, group):
        super().__init__(group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = 0.08

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect((0, 0, width, height)):
            self.kill()


def create_particles(position, group):
    particle_count = 30
    numbers = range(-6, 7)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), group)


if __name__ == '__main__':
    lt = np.array(ImageColor.getcolor('#2C0092', "RGB"))
    rt = np.array(ImageColor.getcolor('#00CFE6', "RGB"))
    lb = np.array(ImageColor.getcolor('#EB2300', "RGB"))
    rb = np.array(ImageColor.getcolor('#FFE600', "RGB"))
    all_sprites = pg.sprite.Group()
    level = Field(5, 7, lt, rt, lb, rb, 'horizontal lines')
    level.set_view(0, 0, (70, 80))
    running = True
    level.render()
    screen2 = pg.Surface(size)
    level_helping = Field(5, 7, lt, rt, lb, rb, 'no_fixed')
    level_helping.set_view(0, 0, (70, 80))
    level_helping.render()
    level_helping.sprite_group1.draw(screen2)
    level.mix_elements()

    fps = 30
    clock = pg.time.Clock()
    create_particles((width // 2, height // 6), all_sprites)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            level.sprite_group1.update(event)
        screen.fill((0, 0, 0))
        level.sprite_group1.draw(screen)
        if [sprite.id for sprite in level.sprite_group2.sprites()] == list(range(1, 5 * 7 + 1)):  # width * height + 1
            all_sprites.update()
            screen.blit(screen2, (0, 0))
            all_sprites.draw(screen)
            t = clock.tick(fps)
            if not all_sprites:
                running = False
        pg.display.flip()
    print('Змечательно! вы завершили уровень!')
    print(level.sprite_group2.sprites()[-1].get_moves())
    count = 0
    pg.quit()
