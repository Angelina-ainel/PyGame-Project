import pygame_textinput
import pygame
pygame.init()

# Create TextInput-object
textinput = pygame_textinput.TextInputVisualizer()

screen = pygame.display.set_mode((1000, 200))
clock = pygame.time.Clock()

while True:
    screen.fill((225, 225, 225))

    events = pygame.event.get()

    # Feed it with events every frame
    textinput.update(events)
    # Blit its surface onto the screen
    screen.blit(textinput.surface, (10, 10))

    for event in events:
        if event.type == pygame.QUIT:
            exit()

    pygame.display.update()
    clock.tick(30)


field_size = tuple(map(int, input().split()))
normal_size = 5, 7
normal_cell_size = 55, 60
quantity = field_size[0] * field_size[1]
if 35 < quantity < 440:
    coeff = (quantity - 35) // (13 + (quantity - 35) // 13)
    cell_size = normal_cell_size[0] - (5 * coeff), normal_cell_size[1] - (5 * coeff)
    print(cell_size)
elif 9 < quantity < 35:
    coeff = (35 - quantity) // (13 + (35 - quantity) // 13)
    cell_size = normal_cell_size[0] + (5 * coeff), normal_cell_size[1] + (5 * coeff)
    print(cell_size)
