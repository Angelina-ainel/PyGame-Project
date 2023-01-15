import sys
import pygame
import time
import os

pygame.init()
pygame.display.set_caption('Цветовые гаммы')
size = width, height = 1000, 750
screen = pygame.display.set_mode(size)

t_font = pygame.font.SysFont('calibri', 60)

current_scene = None


def load_image(name, colorkey=None):
    fullname = os.path.join('test_images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
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


def print_text(text, x, y, font_color=(50, 50, 50), font_type='calibri', font_size=50):
    font_type = pygame.font.SysFont(font_type, font_size)
    button_text = font_type.render(text, True, font_color)
    screen.blit(button_text, (x, y))


class Button:
    def __init__(self, width, height, inactive_color=(255, 192, 203), active_color=(255, 82, 108)):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, text, action=None, font_size=50):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_color, (x, y, self.width, self.height))

            if click[0] == 1:  # здесь будет звук нажатия кнопки
                if action is not None:
                    action()

        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))

        print_text(text, x + 10, y + 10, font_size=font_size)


class Droplist:

    def __init__(self, x, y, w, h, inactive_color, active_color, font, option_list, selected=0):
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.active_color if self.menu_active else self.inactive_color, self.rect)
        pygame.draw.rect(surf, (70, 70, 70), self.rect, 2)
        btn_text = self.font.render(self.option_list[self.selected], 1, (50, 50, 50))
        surf.blit(btn_text, btn_text.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.active_color if i == self.active_option else self.inactive_color, rect)
                btn_text = self.font.render(text, 1, (50, 50, 50))
                surf.blit(btn_text, btn_text.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (70, 70, 70), outer_rect, 2)

    def update(self, event_list):
        m_pos = pygame.mouse.get_pos()
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
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1


def terminate():
    pygame.quit()
    sys.exit()


def menu():
    global t_font
    select_button = Button(470, 65)
    option_button = Button(240, 65)
    quit_button = Button(320, 65)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()

        screen.fill((255, 192, 203))

        text_surface = t_font.render('Цветовые гаммы', True, (50, 50, 50))
        select_button.draw(270, 300, 'Выбрать режим игры', select_menu)
        option_button.draw(370, 400, 'Настройки', options)
        quit_button.draw(335, 500, 'Выйти из игры', terminate)

        screen.blit(text_surface, (280, 100))

        pygame.display.flip()


def select_menu():
    time.sleep(0.1)
    global t_font
    user_options = Button(660, 65, (255, 243, 82), (255, 165, 0))
    off_levels = Button(380, 65, (255, 243, 82), (255, 165, 0))
    back = Button(210, 65, (255, 243, 82), (255, 165, 0))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()

        screen.fill((255, 243, 82))

        user_options.draw(170, 250, 'Задать свои настройки уровня')
        off_levels.draw(290, 350, 'Выбрать уровень', levels)
        back.draw(20, 20, '← Назад', menu)

        pygame.display.flip()


def options():
    time.sleep(0.1)
    global t_font
    back = Button(210, 65, (42, 247, 237), (0, 150, 255))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()

        screen.fill((42, 247, 237))

        text_surface = t_font.render('Настройки', True, (50, 50, 50))
        back.draw(20, 20, '← Назад', menu)

        screen.blit(text_surface, (350, 30))
        pygame.display.flip()


def levels():
    time.sleep(0.1)
    # image = load_image('test_image1.jpg')
    # image_rect = image.get_rect()
    global t_font
    back = Button(210, 65, (102, 255, 102), (50, 205, 50))
    left = Button(330, 50, (102, 255, 102), (50, 205, 50))
    right = Button(315, 50, (102, 255, 102), (50, 205, 50))
    play = Button(180, 50, (102, 255, 102), (50, 205, 50))
    list1 = Droplist(
        800, 20, 160, 40, (102, 255, 102), (50, 205, 50), pygame.font.SysFont('calibri', 30),
        ['beginner', 'easy', 'medium', 'hard', 'expert'])

    while True:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                terminate()

        selected_option = list1.update(event_list)
        if selected_option >= 0:
            print(selected_option)

        screen.fill((102, 255, 102))
        list1.draw(screen)
        back.draw(20, 20, '← Назад', select_menu)
        left.draw(20, 650, '<- Предыдущий уровень', font_size=30)
        right.draw(670, 650, 'Следующий уровень ->', font_size=30)
        play.draw(420, 650, '     Играть', font_size=30)
        # pygame.draw.rect(screen, rect=image_rect, )

        pygame.display.flip()


switch_scene(menu)
current_scene()
