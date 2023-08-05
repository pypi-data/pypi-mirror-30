import pygame

pygame.display.init()

screen = pygame.display.set_mode((400, 300))

background = pygame.Surface((400, 300), flags=pygame.SRCALPHA)
image = pygame.Surface((50, 50), flags=pygame.SRCALPHA)


#####
# Dynamically creating some images, so we don't have to deal with image files.
background.fill((0, 0, 0, 0))
image.fill((0, 0, 0, 0))

pa_background = pygame.PixelArray(background)
pa_image = pygame.PixelArray(image)

for y in range(100, 200):
    for x in range(100, 300):
        if (((x - 100) / 2) + (y - 100)) >= 100:
            pa_background[x, y] = (255, 255, 0)

for y in range(5, 45):
    for x in range(5, 45):
        pa_image[x, y] = (255, 127, 0)

del(pa_background)
del(pa_image)
#
#####


# Make the masks
bg_mask = pygame.mask.from_surface(background)
im_mask = pygame.mask.from_surface(image)


pygame.mouse.set_visible(False)

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

    mouse = pygame.mouse.get_pos()
    overlap = im_mask.overlap_mask(bg_mask, (-mouse[0], -mouse[1]))

    new_image = image.copy()
    for y in range(new_image.get_height()):
        for x in range(new_image.get_width()):
            if overlap.get_at((x, y)):
                new_image.set_at((x, y), (0, 127, 0))

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    screen.blit(new_image, mouse)

    pygame.display.flip()

pygame.quit()
