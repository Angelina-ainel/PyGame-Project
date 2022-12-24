import sys
import pygame

pygame.init()
size = (800, 600)
screen = pygame.display.set_mode(size)

p_font = pygame.font.SysFont('arial', 50)


class Menu:
    def __init__(self):
        self.option_surfaces = []
        self.callbacks = []
        self.option_index = 0

    def append_option(self, option, callback):
        self.option_surfaces.append(p_font.render(option, True, 'black'))
        self.callbacks.append(callback)

    def switch(self, direction):
        self.option_index = max(0, min(self.option_index + direction, len(self.option_surfaces) - 1))

    def select(self):
        self.callbacks[self.option_index]()

    def draw(self, surface, x, y, option_margins):
        for i, opt in enumerate(self.option_surfaces):
            option_rect = opt.get_rect()
            option_rect.topleft = (x, y + i * option_margins)
            if i == self.option_index:
                pygame.draw.rect(surface, (148, 0, 211), option_rect)
            surface.blit(opt, option_rect)


def terminate():
    pygame.quit()
    sys.exit()


menu = Menu()
menu.append_option('Выбрать режим игры', lambda: print('Выбрать режим игры'))
menu.append_option('Настройки', lambda: print('В разработке'))
menu.append_option('Выйти из игры', terminate)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                menu.switch(-1)
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                menu.switch(1)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                menu.select()

    screen.fill((255, 192, 203))
    menu.draw(screen, 150, 200, 75)
    pygame.display.flip()
