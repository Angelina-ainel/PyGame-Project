import sys
import pygame as pg
import time
import os
import sqlite3
import numpy as np
from PIL import ImageColor
import random
from field import Field, Element, Particle, condition_to_mix, create_particles

con = sqlite3.connect('color_schemes.db')
cur = con.cursor()

pg.init()
pg.display.set_caption('Цветовые гаммы')
size = width, height = 1000, 750
screen = pg.display.set_mode(size)

c_font = 'calibri'
up_font = pg.font.SysFont(c_font, 60)

difficulty = {1: 'beginner',
              2: 'easy',
              3: 'normal',
              4: 'hard',
              5: 'expert'}
first_levels = ['beginner_1.jpg', 'easy_4.jpg', 'normal_7.jpg', 'hard_10.jpg', 'expert_13.jpg']
current_levels = ['beginner_1.jpg', 'beginner_2.jpg', 'beginner_3.jpg', 'beginner_16.jpg', 'beginner_17.jpg']
c = 0
current_level = current_levels[c]

count_moves = 0

next_count = 0
previous_count = 0

current_scene = None


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


def switch_scene(scene):
    global current_scene
    current_scene = scene


def print_text(text, x, y, font_color=(50, 50, 50), font_type=c_font, font_size=50):
    font_type = pg.font.SysFont(font_type, font_size)
    button_text = font_type.render(text, True, font_color)
    screen.blit(button_text, (x, y))


class Button:
    def __init__(self, width, height, inactive_color=(255, 192, 203), active_color=(255, 82, 108)):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, text, action=None, font_size=50):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pg.draw.rect(screen, self.active_color, (x, y, self.width, self.height))

            if click[0] == 1:  # здесь будет звук нажатия кнопки
                if action is not None:
                    action()

        else:
            pg.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))

        print_text(text, x + 10, y + 10, font_size=font_size)


# class ColorButton(Button):


class Droplist:
    def __init__(self, x, y, w, h, inactive_color, active_color, font, option_list, selected=0):
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.rect = pg.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pg.draw.rect(surf, self.active_color if self.menu_active else self.inactive_color, self.rect)
        pg.draw.rect(surf, (70, 70, 70), self.rect, 2)
        btn_text = self.font.render(self.option_list[self.selected], 1, (50, 50, 50))
        surf.blit(btn_text, btn_text.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pg.draw.rect(surf, self.active_color if i == self.active_option else self.inactive_color, rect)
                btn_text = self.font.render(text, 1, (50, 50, 50))
                surf.blit(btn_text, btn_text.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pg.draw.rect(surf, (70, 70, 70), outer_rect, 2)

    def update(self, event_list):
        m_pos = pg.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(m_pos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(m_pos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1


COLOR_INACTIVE_S_U = pg.Color((204, 102, 0))
COLOR_ACTIVE_S_U = pg.Color((70, 70, 70))
FONT = pg.font.SysFont(c_font, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE_S_U
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE_S_U if self.active else COLOR_INACTIVE_S_U
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)


def terminate():
    pg.quit()
    sys.exit()


def next_counter():
    global next_count
    next_count = 1
    time.sleep(0.25)


def previous_counter():
    global previous_count
    previous_count = 1
    time.sleep(0.25)


def game():
    global screen
    back = Button(50, 50, (0, 0, 0), (255, 231, 189))
    query = '''SELECT levels.left_top, levels.right_top, levels.left_bottom, levels.right_bottom, levels.size, 
levels.cell_size, templates.type, difficulties.difficulty
FROM levels INNER JOIN templates ON templates.id = levels.template
INNER JOIN difficulties ON difficulties.id = levels.difficulty
WHERE levels.difficulty = (SELECT difficulties.id WHERE difficulties.difficulty = ?) AND levels.id = ?'''
    pg.init()
    difficulty, id = current_level[:-4].split('_')
    res = cur.execute(query, (difficulty, int(id))).fetchone()
    all_sprites = pg.sprite.Group()
    field_size = tuple(map(int, res[4].split('*')))
    cell_size = tuple(map(lambda x: int(x) * 2, res[5].split('*')))
    screen_size = w, h = cell_size[0] * field_size[0], cell_size[1] * field_size[1] + 150
    screen = pg.display.set_mode(screen_size)

    left_top = np.array(ImageColor.getcolor(res[0], "RGB"))
    right_top = np.array(ImageColor.getcolor(res[1], "RGB"))
    left_bottom = np.array(ImageColor.getcolor(res[2], "RGB"))
    right_bottom = np.array(ImageColor.getcolor(res[3], "RGB"))
    scheme = Field(*field_size, left_top, right_top, left_bottom, right_bottom, res[6])
    scheme.set_view(0, 75, cell_size)
    scheme.render()
    screen2 = pg.Surface(screen_size)
    scheme_helping = Field(*field_size, left_top, right_top, left_bottom, right_bottom, 'no_fixed')
    scheme_helping.set_view(0, 75, cell_size)
    scheme_helping.render()
    scheme_helping.sprite_group1.draw(screen2)
    scheme.mix_elements()
    fps = 30
    clock = pg.time.Clock()
    create_particles((w // 2, h // 6), all_sprites)
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                screen = pg.display.set_mode(size)
                switch_scene(levels)
                levels()
            scheme.sprite_group1.update(event)
        screen.fill((0, 0, 0))
        scheme.sprite_group1.draw(screen)
        back.draw(w - 70, 10, '← Назад', levels)
        if [sprite.id for sprite in scheme.sprite_group2.sprites()] == \
                list(range(1, field_size[0] * field_size[1] + 1)):  # width * height + 1

            all_sprites.update()
            screen.blit(screen2, (0, 0))

            all_sprites.draw(screen)
            clock.tick(fps)
            if not all_sprites:
                screen = pg.display.set_mode(size) # это убрать здесь
                switch_scene(levels) #
                levels() #
                print(count_moves)
                # вот здесь должен появляться результат пользователя(count_moves) и поощрительные слова,
                # а потом при нажатии на какую-нибудь кнопку назад возврашение на levels
        pg.display.flip()
    # print(count_moves)


def menu():
    select_button = Button(470, 65)
    option_button = Button(240, 65)
    quit_button = Button(320, 65)

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                terminate()

        screen.fill((255, 192, 203))

        up_text = up_font.render('Цветовые гаммы', True, (50, 50, 50))
        select_button.draw(270, 300, 'Выбрать режим игры', select_menu)
        option_button.draw(370, 400, 'Настройки', options)
        quit_button.draw(335, 500, 'Выйти из игры', terminate)

        screen.blit(up_text, (283, 100))

        pg.display.flip()


def select_menu():
    time.sleep(0.25)
    user_options = Button(660, 65, (255, 243, 82), (255, 165, 0))
    off_levels = Button(380, 65, (255, 243, 82), (255, 165, 0))
    back = Button(210, 65, (255, 243, 82), (255, 165, 0))

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                terminate()

        screen.fill((255, 243, 82))

        user_options.draw(170, 250, 'Задать свои настройки уровня', user_level)
        off_levels.draw(290, 350, 'Выбрать уровень', levels)
        back.draw(20, 20, '← Назад', menu)

        pg.display.flip()


def user_level():
    time.sleep(0.25)
    global up_font, c_font
    down_font = pg.font.SysFont(c_font, 30)

    back = Button(210, 65, (255, 168, 18), (204, 102, 0))

    field_size_text = down_font.render('Размер поля', True, (50, 50, 50))
    field_size_text1 = down_font.render('в клетках:', True, (50, 50, 50))
    input_box1 = InputBox(170, 180, 50, 32)
    input_box2 = InputBox(170, 235, 50, 32)
    input_boxes = [input_box1, input_box2]
    w_text = down_font.render('Ширина =', True, (50, 50, 50))
    h_text = down_font.render('Высота =', True, (50, 50, 50))

    drop_list_text = down_font.render('Выберите шаблон поля:', True, (50, 50, 50))
    query = '''SELECT type FROM templates'''
    res = cur.execute(query).fetchall()
    templates_list = []
    for r in res:
        r = r[0]
        templates_list.append(r)
    drop_list = Droplist(
        70, 350, 210, 40, (255, 168, 18), COLOR_INACTIVE_S_U, pg.font.SysFont(c_font, 30),
        templates_list)
    clock = pg.time.Clock()
    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                terminate()

            for box in input_boxes:
                box.handle_event(event)
        selected_option = drop_list.update(events)
        if selected_option >= 0:
            print(templates_list[selected_option])

        for box in input_boxes:
            box.update()

        screen.fill((255, 168, 18))

        for box in input_boxes:
            box.draw(screen)
        up_text = up_font.render('Создайте свой уровень', True, (50, 50, 50))
        back.draw(20, 20, '← Назад', select_menu)

        drop_list.draw(screen)
        screen.blit(drop_list_text, (30, 300))

        screen.blit(up_text, (250, 25))

        screen.blit(field_size_text, (100, 100))
        screen.blit(field_size_text1, (110, 130))
        screen.blit(w_text, (30, 180))
        screen.blit(h_text, (30, 235))

        pg.display.flip()
        clock.tick(30)


def options():
    time.sleep(0.25)
    global up_font
    back = Button(210, 65, (42, 247, 237), (0, 150, 255))

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                terminate()

        screen.fill((42, 247, 237))

        text_surface = up_font.render('Настройки', True, (50, 50, 50))
        back.draw(20, 20, '← Назад', menu)

        screen.blit(text_surface, (350, 30))
        pg.display.flip()


def levels():
    time.sleep(0.25)
    global cur, next_count, previous_count, current_level, current_levels, c, screen
    screen = pg.display.set_mode(size)
    back = Button(210, 65, (102, 255, 102), (50, 205, 50))
    left = Button(330, 50, (102, 255, 102), (50, 205, 50))
    right = Button(315, 50, (102, 255, 102), (50, 205, 50))
    play = Button(180, 50, (102, 255, 102), (50, 205, 50))
    query = '''SELECT difficulty FROM difficulties'''
    res = cur.execute(query).fetchall()
    templates_list = []
    for r in res:
        r = r[0]
        templates_list.append(r)
    list1 = Droplist(
        800, 20, 160, 40, (102, 255, 102), (50, 205, 50), pg.font.SysFont(c_font, 30),
        templates_list)

    while True:
        event_list = pg.event.get()
        for event in event_list:
            if event.type == pg.QUIT:
                terminate()

        selected_option = list1.update(event_list) + 1
        query = '''SELECT id FROM levels WHERE difficulty = ?'''
        res = cur.execute(query, (selected_option,)).fetchall()
        if selected_option > 0:
            current_levels = []
            c = 0
            next_count = 0
            previous_count = 0
            dif_str = difficulty[selected_option]
            for r in res:
                result = f'{dif_str}_{str(r[0])}.jpg'
                current_levels.append(result)
            current_level = current_levels[c]
        if current_level != current_levels[-1] and next_count > 0:
            c += 1
            current_level = current_levels[c]
            next_count = 0
        elif current_level == current_levels[-1] and next_count > 0:
            c = len(current_levels) - 1
            next_count = 0
        flag = False
        for c_l in first_levels:
            if current_level == c_l:
                flag = True
        if flag and previous_count > 0:
            c = 0
            previous_count = 0
            flag = False
        elif not flag and previous_count > 0:
            c -= 1
            current_level = current_levels[c]
            previous_count = 0

        screen.fill((102, 255, 102))
        list1.draw(screen)
        back.draw(20, 20, '← Назад', select_menu)
        left.draw(20, 650, '<- Предыдущий уровень', font_size=30, action=previous_counter)
        right.draw(670, 650, 'Следующий уровень ->', font_size=30, action=next_counter)
        right_levels = ['beginner_1.jpg', 'beginner_2.jpg', 'beginner_3.jpg']
        not_right_levels = ['beginner_16.jpg', 'beginner_17.jpg', 'beginner_18.jpg', 'beginner_19.jpg']
        es_n_levels = ['easy_4.jpg', 'easy_5.jpg', 'easy_6.jpg', 'normal_7.jpg', 'normal_8.jpg', 'normal_9.jpg']
        if current_level in right_levels:
            s = current_level.split('.')
            s = s[0][-1]
            text_surface = up_font.render(f'Уровень {s}', True, (50, 50, 50))
            screen.blit(text_surface, (375, 20))
        elif current_level in not_right_levels:
            s = current_level.split('.')
            s = s[0][-2:]
            text_surface = up_font.render(f'Уровень {int(s) - 12}', True, (50, 50, 50))
            screen.blit(text_surface, (375, 20))
        elif current_level in es_n_levels:
            s = current_level.split('.')
            s = s[0][-1]
            text_surface = up_font.render(f'Уровень {int(s) + 4}', True, (50, 50, 50))
            screen.blit(text_surface, (375, 20))
        else:
            s = current_level.split('.')
            s = s[0][-2:]
            text_surface = up_font.render(f'Уровень {int(s) + 4}', True, (50, 50, 50))
            screen.blit(text_surface, (375, 20))
        play.draw(420, 650, '     Играть', game, font_size=30)
        image = load_image(current_level)

        x, y = 350, 140
        w, h = 320, 470
        border = 3

        pg.draw.rect(screen, (0, 0, 0), (x, y, w, h))
        pg.draw.rect(screen, (102, 255, 102), (x + border, y + border, w - border * 2, h - border * 2))

        screen.blit(image, (360, 150))

        pg.display.flip()


switch_scene(menu)
current_scene()
