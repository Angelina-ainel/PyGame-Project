import sys
import pygame as pg
import time
import os
import sqlite3
import numpy as np
from PIL import ImageColor
from field import Field, create_particles

con = sqlite3.connect('color_schemes.db')
cur = con.cursor()

difficulty = {1: 'beginner',
              2: 'easy',
              3: 'normal',
              4: 'hard',
              5: 'expert'}

#  initial choice of difficulty and first level
query = '''SELECT id FROM levels WHERE difficulty = 1'''
res = cur.execute(query).fetchall()
current_levels = []
c = 0
for r in res:
    r = f'{difficulty[1]}_{str(r[0])}.jpg'
    current_levels.append(r)
current_level = current_levels[c]

pg.init()
pg.display.set_caption('Цветовые гаммы')
size = width, height = 1000, 750
screen = pg.display.set_mode(size)

c_font = 'calibri'
up_font = pg.font.SysFont(c_font, 60)
down_font = pg.font.SysFont(c_font, 30)

next_count = 0
previous_count = 0

current_scene = None

width_input = 3
height_input = 3
selected_template = '4 corners'
mistake = False


def music_play():
    pg.mixer.music.play(-1)


def music_up():  # turn up the music volume
    global vol
    if vol < 1:
        vol += 0.01
    pg.mixer.music.set_volume(vol)


def music_down():  # turn down the music volume
    global vol
    if vol > 0:
        vol -= 0.01
    pg.mixer.music.set_volume(vol)


pg.mixer.music.load("data/ambient-sleep-music-food-for-the-soul.mp3")
vol = 0.5
pg.mixer.music.set_volume(vol)
music_play()


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


class Button:  # create buttons
    def __init__(self, width, height, inactive_color=(255, 192, 203), active_color=(255, 82, 108)):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, text, action=None, font_size=50):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:  # drawing a button with an active color
            pg.draw.rect(screen, self.active_color, (x, y, self.width, self.height))

            if click[0] == 1:
                if action is not None:
                    action()

        else:  # drawing a button with an inactive color
            pg.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))

        print_text(text, x + 10, y + 10, font_size=font_size)


class ColorButton(Button):  # create colored buttons in user_level()
    def __init__(self, width, height, inactive_color, active_color):
        super().__init__(width, height, inactive_color, active_color)
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, text, action=None, font_size=50):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        global color_list, down_font

        #  draw a button with an active color
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height and click[0] == 1:
            pg.draw.rect(screen, self.active_color, (x, y, self.width, self.height))

            if self.active_color not in color_list:
                if len(color_list) < 4:
                    color_list.append(self.active_color)
                    time.sleep(0.3)

                else:
                    color_list.remove(color_list[0])
                    color_list.append(self.active_color)
                    time.sleep(0.3)

        else:  # draw a button with an inactive color
            pg.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))


color_list = []


class Droplist:  # create droplist in user_level()
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

        if self.draw_menu:  # draw a drop list if the menu is open
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


COLOR_INACTIVE_S_U = pg.Color((109, 49, 135))
COLOR_ACTIVE_S_U = pg.Color((70, 70, 70))
FONT = pg.font.SysFont(c_font, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE_S_U
        self.text = str(text)
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:  # changes the color of the frames
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE_S_U if self.active else COLOR_INACTIVE_S_U
        if event.type == pg.KEYDOWN:  # writes the text entered by the user
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += str(event.unicode)
                self.txt_surface = FONT.render(self.text, True, self.color)
        if not str(self.text).isdigit():  # checking for numbers
            self.text = ''
            self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pg.draw.rect(screen, self.color, self.rect, 2)


def terminate():
    pg.quit()
    sys.exit()


def next_counter():  # Moving to the next level
    global next_count
    next_count = 1
    time.sleep(0.25)


def previous_counter():  # Moving to the previous level
    global previous_count
    previous_count = 1
    time.sleep(0.25)


def result(width, height, moves, inserting, level_id=1):
    global screen, up_font
    up_font = pg.font.SysFont(c_font, 45)
    screen = pg.display.set_mode((width, height))
    window_size = w, h = width, height * 0.75  # окно с результатом красивого размера
    moves_int = moves
    result = pg.Surface(window_size)
    back = Button(200, 70, (255, 231, 185), (255, 198, 169))
    if inserting:  # если уровень из базы данных, то в столбец moves вставляется это значение
        query = """UPDATE levels
        SET moves = ?
        WHERE levels.id = ?"""
        cur.execute(query, (moves_int, level_id))
        con.commit()
    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                terminate()
        screen.fill((0, 0, 0))
        result.fill((255, 231, 189))
        level_passed = up_font.render('Уровень пройден!', True, (50, 50, 50))
        text = f'Ходов: {moves_int}'
        moves = up_font.render(text, True, (50, 50, 50))
        result.blit(level_passed, (20, h // 3))
        result.blit(moves, (20, h // 2))
        screen.blit(result, (0, height // 8))
        if inserting:  # возврат на разные сцены
            back.draw(w - 200, h - 10, '← Назад', levels)
        else:
            back.draw(w - 200, h - 10, '← Назад', user_level)
        pg.display.flip()


def conditions(w_input, h_input, colors):
    if not w_input or not h_input or not colors:
        return False
    elif int(width_input) not in range(3, 21) or int(height_input) not in range(3, 21) or \
            len(color_list) < 4:
        return False
    return True


def user_game():
    global screen, width_input, height_input, selected_template, color_list, mistake
    if not conditions(width_input, height_input, color_list):  # если данные некорректны, на экран выводится
        mistake = True  # уровень не создастся
        switch_scene(user_level)
        user_level()
    mistake = False
    back = Button(50, 50, (0, 0, 0), (195, 138, 219))
    wi, hei = int(width_input), int(height_input)
    field_size = wi, hei
    quantity = wi * hei
    coeff = abs(quantity - 35) // (13 + 2 * (quantity - 35) // 30)
    if quantity >= 35:  # автоматический расчёт размеров клетки на основе введённых размеров поля
        cell_size = (55 - (5 * coeff)) * 2, (60 - (5 * coeff)) * 2  # относительно поля 5*7 и размера клетки 55*60 пикс.
    else:
        cell_size = (55 + (5 * coeff)) * 2, (60 + (5 * coeff)) * 2
    screen_size = x, y = cell_size[0] * field_size[0], cell_size[1] * field_size[1] + 150
    screen = pg.display.set_mode(screen_size)

    all_sprites = pg.sprite.Group()
    left_top = np.array(color_list[0])
    right_top = np.array(color_list[1])
    left_bottom = np.array(color_list[2])
    right_bottom = np.array(color_list[3])
    scheme = Field(*field_size, left_top, right_top, left_bottom, right_bottom, selected_template)
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
    create_particles((x // 2, y // 6), all_sprites)
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # screen = pg.display.set_mode(size)
                switch_scene(user_level)
                user_level()
            scheme.sprite_group1.update(event)
        screen.fill((0, 0, 0))
        scheme.sprite_group1.draw(screen)
        back.draw(x - 70, 10, '←', user_level)
        if [sprite.id for sprite in scheme.sprite_group2.sprites()] == \
                list(range(1, field_size[0] * field_size[1] + 1)):  # width * height + 1
            all_sprites.update()
            screen.blit(screen2, (0, 0))
            all_sprites.draw(screen)
            clock.tick(fps)
            if not all_sprites:  # сохранение изображения законченного уровня на память в папу data
                screen3 = pg.Surface((wi * cell_size[0], hei * cell_size[1]))
                scheme.set_view(0, 0, cell_size)
                scheme.render()
                scheme.sprite_group1.draw(screen3)
                image = pg.transform.scale(screen3, (300, 450))
                if any(map(lambda img: img.startswith('user_level'), os.listdir('data'))):
                    numbers = [int(n[11:-4]) for n in  # сохранение с увеличивющимися порядковыми номерами
                               filter(lambda file: file.startswith('user_level'), os.listdir('data'))]
                    pg.image.save(image, 'data/' + 'user_level_' + str(max(numbers) + 1) + '.jpg')
                else:
                    pg.image.save(image, 'data/' + 'user_level_1' + '.jpg')
                switch_scene(result(x, y, scheme.sprite_group2.sprites()[-1].get_moves(), False))
                result(x, y, scheme.sprite_group2.sprites()[-1].get_moves(), False)
        pg.display.flip()


def game():
    global screen
    back = Button(50, 50, (0, 0, 0), (255, 231, 189))
    query = '''SELECT levels.left_top, levels.right_top, levels.left_bottom, levels.right_bottom, levels.size, 
levels.cell_size, templates.type, difficulties.difficulty
FROM levels INNER JOIN templates ON templates.id = levels.template
INNER JOIN difficulties ON difficulties.id = levels.difficulty
WHERE levels.difficulty = (SELECT difficulties.id WHERE difficulties.difficulty = ?) AND levels.id = ?'''
    difficulty, id = current_level[:-4].split('_')  # создание гаммы из бд по id и сложности из названия файла
    res = cur.execute(query, (difficulty, int(id))).fetchone()
    all_sprites = pg.sprite.Group()
    field_size = tuple(map(int, res[4].split('*')))
    cell_size = tuple(map(lambda x: int(x) * 2, res[5].split('*')))
    screen_size = w, h = cell_size[0] * field_size[0], cell_size[1] * field_size[1] + 150
    screen = pg.display.set_mode(screen_size)  # размер окна, соответствующий размеру игрового поля

    left_top = np.array(ImageColor.getcolor(res[0], "RGB"))  # преобразование HEX-формата цвета в RGB с помощью pillow
    right_top = np.array(ImageColor.getcolor(res[1], "RGB"))
    left_bottom = np.array(ImageColor.getcolor(res[2], "RGB"))
    right_bottom = np.array(ImageColor.getcolor(res[3], "RGB"))
    scheme = Field(*field_size, left_top, right_top, left_bottom, right_bottom, res[6])
    scheme.set_view(0, 75, cell_size)
    scheme.render()
    screen2 = pg.Surface(screen_size)  # вспомогательный холст и гамма, для правильного отображения разлетающихся звёзд
    scheme_helping = Field(*field_size, left_top, right_top, left_bottom, right_bottom,  # после завершения уровня
                           'no_fixed')
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
        back.draw(w - 70, 10, '←', levels)
        if [sprite.id for sprite in scheme.sprite_group2.sprites()] == list(
                range(1, field_size[0] * field_size[1] + 1)):  # width * height + 1
            all_sprites.update()  # если в группе спрайты следуют по порядку, то запускается салют
            screen.blit(screen2, (0, 0))   # в честь завршения уровня
            all_sprites.draw(screen)
            clock.tick(fps)
            if not all_sprites:
                switch_scene(result(w, h, scheme.sprite_group2.sprites()[-1].get_moves(), True, level_id=id))
                result(w, h, scheme.sprite_group2.sprites()[-1].get_moves(), True, level_id=id)  # показ результата
        pg.display.flip()


def menu():  # draw main menu
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


def select_menu():  # draws a menu for selecting game modes
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


def user_level():  # draws a level creation menu
    time.sleep(0.25)
    global up_font, c_font, down_font, width_input, height_input, selected_template, screen, mistake
    screen = pg.display.set_mode(size)
    back = Button(210, 65, (185, 128, 209), (109, 49, 135))
    mistake_message = down_font.render('Укажите правильные данные!', True, (50, 50, 50))
    field_size_text = down_font.render('Размер поля', True, (50, 50, 50))
    field_size_text1 = down_font.render('в клетках:', True, (50, 50, 50))
    field_size_text2 = down_font.render('(Минимум 3, максимум 20)', True, (50, 50, 50))
    input_box1 = InputBox(170, 210, 50, 32)
    input_box2 = InputBox(170, 265, 50, 32)
    input_boxes = [input_box1, input_box2]
    w_text = down_font.render('Ширина =', True, (50, 50, 50))
    h_text = down_font.render(' Высота  =', True, (50, 50, 50))

    drop_list_text = down_font.render('Выберите шаблон поля:', True, (50, 50, 50))
    query = '''SELECT type FROM templates'''
    res = cur.execute(query).fetchall()
    templates_list = []
    for r in res:
        r = r[0]
        templates_list.append(r)
    drop_list = Droplist(
        440, 150, 210, 40, (185, 128, 209), COLOR_INACTIVE_S_U, pg.font.SysFont(c_font, 30),
        templates_list)

    select_color_text = down_font.render('Выберите 4 цвета:', True, (50, 50, 50))
    red_button = ColorButton(70, 70, (255, 0, 0), (255, 0, 0))
    yellow_button = ColorButton(70, 70, (255, 255, 0), (255, 255, 0))
    dark_blue_button = ColorButton(70, 70, (0, 0, 255), (0, 0, 255))
    blue_button = ColorButton(70, 70, (15, 147, 255), (15, 147, 255))
    dark_green_button = ColorButton(70, 70, (0, 128, 0), (0, 128, 0))
    pink_button = ColorButton(70, 70, (255, 92, 119), (255, 92, 119))
    orange_button = ColorButton(70, 70, (255, 165, 0), (255, 165, 0))
    brown_button = ColorButton(70, 70, (101, 67, 33), (101, 67, 33))
    violet_button = ColorButton(70, 70, (139, 0, 255), (139, 0, 255))
    light_green_button = ColorButton(70, 70, (0, 255, 0), (0, 255, 0))
    pink_forest_button = ColorButton(70, 70, (101, 0, 1), (101, 0, 1))
    spring_green_button = ColorButton(70, 70, (0, 250, 154), (0, 250, 154))
    light_blue_button = ColorButton(70, 70, (135, 206, 250), (135, 206, 250))
    green_button = ColorButton(70, 70, (0, 179, 0), (0, 179, 0))
    dark_violet_button = ColorButton(70, 70, (79, 0, 112), (79, 0, 112))

    select_colors = down_font.render(' Выбранные цвета:', True, (50, 50, 50))

    create = Button(200, 65, (185, 128, 209), (109, 49, 135))

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
            option = templates_list[selected_option]
            selected_template = option

        for box in input_boxes:
            box.update()

        screen.fill((185, 128, 209))

        for box in input_boxes:
            box.draw(screen)
        up_text = up_font.render('Создайте свой уровень', True, (50, 50, 50))
        back.draw(20, 20, '← Назад', select_menu)
        width_input = input_box1.text  # получение текста из полей для ввода
        height_input = input_box2.text
        create.draw(730, 600, 'Создать', user_game)
        drop_list.draw(screen)
        screen.blit(drop_list_text, (400, 100))

        screen.blit(select_color_text, (100, 340))
        red_button.draw(30, 400, '')
        yellow_button.draw(110, 400, '')
        dark_blue_button.draw(190, 400, '')
        blue_button.draw(270, 400, '')
        dark_green_button.draw(350, 400, '')

        pink_forest_button.draw(30, 500, '')
        spring_green_button.draw(110, 500, '')
        light_blue_button.draw(190, 500, '')
        green_button.draw(270, 500, '')
        dark_violet_button.draw(350, 500, '')

        pink_button.draw(30, 600, '')
        orange_button.draw(110, 600, '')
        brown_button.draw(190, 600, '')
        violet_button.draw(270, 600, '')
        light_green_button.draw(350, 600, '')

        screen.blit(select_colors, (710, 340))
        x = 680
        for color in color_list:  # draws the selected colors
            button = ColorButton(70, 70, color, color)
            button.draw(x, 400, '')
            x += 80

        if mistake:  # вывод сообщения об ошибке
            screen.blit(mistake_message, (width - 400, height - 50))

        screen.blit(up_text, (250, 25))

        screen.blit(field_size_text, (100, 100))
        screen.blit(field_size_text1, (110, 130))
        screen.blit(field_size_text2, (30, 160))
        screen.blit(w_text, (30, 210))
        screen.blit(h_text, (30, 265))

        pg.display.flip()
        clock.tick(30)


def options():  # draw music options
    time.sleep(0.25)
    global up_font, vol
    back = Button(210, 65, (42, 247, 237), (0, 150, 255))
    up = Button(240, 65, (42, 247, 237), (0, 150, 255))
    down = Button(260, 65, (42, 247, 237), (0, 150, 255))

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                terminate()

        screen.fill((42, 247, 237))

        text_surface = up_font.render('Настройки', True, (50, 50, 50))
        text_surface1 = up_font.render('Настройте громкость', True, (50, 50, 50))
        text_surface2 = up_font.render('музыки:', True, (50, 50, 50))
        mus_vol = up_font.render(str(round(vol, 2)), True, (50, 50, 50))  # writes the music volume value

        back.draw(20, 20, '← Назад', menu)
        up.draw(380, 370, 'Увеличить', music_up)
        down.draw(380, 460, 'Уменьшить', music_down)

        screen.blit(text_surface, (350, 30))
        screen.blit(text_surface1, (240, 140))
        screen.blit(text_surface2, (400, 180))
        screen.blit(mus_vol, (450, 270))
        pg.display.flip()


def levels():  # draw menu levels
    time.sleep(0.25)
    global cur, next_count, previous_count, screen, current_level, current_levels, c

    # creates a list of the first levels
    fl_count = 1
    first_levels = []
    for k_diff in range(5):
        k_diff += 1
        result = f'{difficulty[k_diff]}_{fl_count}.jpg'
        fl_count += 3
        first_levels.append(result)

    screen = pg.display.set_mode(size)
    back = Button(210, 65, (102, 255, 102), (50, 205, 50))
    left = Button(330, 50, (102, 255, 102), (50, 205, 50))
    right = Button(315, 50, (102, 255, 102), (50, 205, 50))
    play = Button(180, 50, (102, 255, 102), (50, 205, 50))

    # filling in the drop list
    query1 = '''SELECT difficulty FROM difficulties'''
    res = cur.execute(query1).fetchall()
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

        # user's choice of difficulty and level
        selected_option = list1.update(event_list) + 1  # the number of the selected difficulty
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

        # switching between levels
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
        left.draw(20, 650, '<- Предыдущий уровень', previous_counter, font_size=30)
        right.draw(670, 650, 'Следующий уровень ->', next_counter, font_size=30)

        # visual numbering of levels
        n_cur_l = 1
        for count, level in enumerate(current_levels):
            if current_level == level:
                n_cur_l = count + 1
        text_surface = up_font.render(f'Уровень {n_cur_l}', True, (50, 50, 50))
        screen.blit(text_surface, (385, 20))

        play.draw(420, 650, '     Играть', game, font_size=30)
        image = load_image(current_level)

        x, y = 350, 140
        w, h = 320, 470
        border = 3

        pg.draw.rect(screen, (0, 0, 0), (x, y, w, h))
        # drawing a black frame behind the level image
        pg.draw.rect(screen, (102, 255, 102), (x + border, y + border, w - border * 2, h - border * 2))

        screen.blit(image, (360, 150))

        pg.display.flip()


switch_scene(menu)
current_scene()
