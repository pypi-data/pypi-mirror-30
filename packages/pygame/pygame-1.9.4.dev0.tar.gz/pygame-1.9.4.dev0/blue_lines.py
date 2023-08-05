import pygame, sys
screen = pygame.display.set_mode((200,200))
offscreen = screen.convert()
# offscreen = pygame.Surface(screen.get_size())
print(offscreen)
print(offscreen.get_flags())
print(offscreen.get_losses())
print(offscreen.get_shifts())
print(offscreen.get_masks())
offscreen.fill((255, 255, 255))
going = True

print(offscreen.map_rgb((0, 0, 255, 0)))
print(offscreen.map_rgb((0, 0, 255, 0)))

while going:
    for event in pygame.event.get():
        if ((event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or
            event.type == pygame.QUIT):
            going = False

    screen.fill((0,0,0))
    # offscreen.fill((0,0,0))
    # offscreen.fill((255, 255, 255))
    offscreen.fill((1, 1, 1))
    if 0:
        pygame.draw.aalines(screen, (0, 0, 255), False, [(0,0), (100,100), (100, 200)])
        pygame.draw.line(screen, (0, 0, 255), (0,100), (100,200), 2)
    else:
        # pygame.draw.aalines(offscreen, (255, 255, 255), False, [(0,0), (100,100), (100, 200)])
        # pygame.draw.aalines(offscreen, (0, 255, 0), False, [(20,20), (0,50), (0, 50)])
        # pygame.draw.aalines(offscreen, (0, 0, 255), False, [(30,30), (70,90), (80, 100)])
        pygame.draw.aaline(offscreen, (200, 0, 0, 127), (20,40), (60,100))
        pygame.draw.aaline(offscreen, (0, 200, 0, 127), (40,40), (80,100))
        pygame.draw.aaline(offscreen, (0, 0, 200, 127), (100,40), (120,100))

        # pygame.draw.line(offscreen, (200, 200, 200), (40,40), (80,100))
        # pygame.draw.line(offscreen, (0, 0, 255), (0,100), (100,200), 2)
        screen.blit(offscreen, (0,0))

    pygame.display.flip()
    pygame.time.Clock().tick(30)