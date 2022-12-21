# print('there will be an interface for menu and everything else')
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


menu = Menu()
menu.append_option('Цветовые гаммы', lambda: print('Цветовые гаммы'))
menu.append_option('Выйти из игры', pygame.quit)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                menu.switch(-1)
            elif event.key == pygame.K_s:
                menu.switch(1)
            elif event.key == pygame.K_SPACE:
                menu.select()

    screen.fill((255, 240, 245))
    menu.draw(screen, 100, 100, 75)
    pygame.display.flip()
pygame.quit()
