import sys, pygame
from pygame.locals import *
from pygame import freetype

pygame.init()
def wait_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                pygame.quit()
                sys.exit()


screen = pygame.display.set_mode((150, 100))
screen.fill((255,255,255))

font = freetype.Font(None, size=50)
font.origin = True
font.kerning = True # uncomment this to get the crash
text_surf, text_rect = font.render('Hello', (0,0,0), size=50)

screen.blit(text_surf, (0,0))

pygame.display.flip()
wait_key()
