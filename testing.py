import pygame

pygame.init()
pygame.display.set_caption('Перетаскивание')
size = width, height = 300, 300
screen = pygame.display.set_mode(size)
running = True
x, y = 0, 0
pushed = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if x < event.pos[0] < x + 100 and y < event.pos[1] < y + 100:
                pushed = True
        if event.type == pygame.MOUSEBUTTONUP:
            pushed = False
        if event.type == pygame.MOUSEMOTION:
            if pushed:
                print(event.pos)
                if width - event.pos[0] > 0 and height - event.pos[1] > 0:
                    dx, dy = event.rel
                    x += dx
                    y += dy
    screen.fill(pygame.Color('black'))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, 100, 100))
    pygame.display.flip()
pygame.quit()
