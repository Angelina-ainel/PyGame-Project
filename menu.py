import sys
import pygame

pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)

t_font = pygame.font.SysFont('calibri', 50)

current_scene = None


def switch_scene(scene):
    global current_scene
    current_scene = scene


def print_text(text, x, y, font_color=(50, 50, 50), font_type='calibri', font_size=40):
    font_type = pygame.font.SysFont(font_type, font_size)
    button_text = font_type.render(text, True, font_color)
    screen.blit(button_text, (x, y))


class Button:
    def __init__(self, width, height, inactive_color=(255, 192, 203), active_color=(255, 82, 108)):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, text, action=None, font_size=40):
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


def terminate():
    pygame.quit()
    sys.exit()


def menu():
    global t_font
    select_button = Button(375, 60)
    option_button = Button(205, 60)
    quit_button = Button(265, 60)

    run = True
    while run:

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
                switch_scene(None)

        screen.fill((255, 192, 203))

        text_surface = t_font.render("Цветовые гаммы", True, (50, 50, 50))
        select_button.draw(225, 200, 'Выбрать режим игры', select_menu)
        option_button.draw(290, 300, 'Настройки', options)
        quit_button.draw(270, 400, 'Выйти из игры', terminate)

        screen.blit(text_surface, (230, 50))

        pygame.display.flip()


def select_menu():
    global t_font
    user_options = Button(530, 60, (255, 243, 82), (255, 165, 0))
    off_levels = Button(310, 60, (255, 243, 82), (255, 165, 0))
    back = Button(180, 60, (255, 243, 82), (255, 165, 0))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
                switch_scene(None)

        screen.fill((255, 243, 82))

        user_options.draw(130, 250, 'Задать свои настройки уровня')
        off_levels.draw(225, 350, 'Выбрать уровень')
        back.draw(20, 20, '← Назад', menu)

        pygame.display.flip()


def options():
    global t_font
    back = Button(180, 60, (42, 247, 237), (0, 150, 255))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
                switch_scene(None)

        screen.fill((42, 247, 237))

        back.draw(20, 20, '← Назад', menu)

        pygame.display.flip()


switch_scene(menu)
while current_scene is not None:
    current_scene()
