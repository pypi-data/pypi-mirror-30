import pygame as pg
from pygame import SRCALPHA, Surface, init
from pygame.display import set_mode

init()
screen = set_mode()


"""
    "dest_surf",
    "surf",
    "search_color",
    "threshold",
    "set_color",
    "set_behavior",
    "search_surf",
    "inverse_set",
"""

dest_surf = Surface((32,32), SRCALPHA, 32)
dest_surf.fill((255,255,255))
surf = Surface((32,32), SRCALPHA, 32)
surf.fill((40,40,40))

search_color = (30, 30, 30)
threshold = (11,11,11)
set_color = (255,0,0)
set_behavior = 2

num_threshold_pixels = pg.transform.threshold(dest_surf, surf, search_color)

# set the similar pixels in destination surface to the color
#     in the first surface.

# num_threshold_pixels = threshold(
#     dest_surface,
#     surface,
#     search_color,
#     the_threshold,
#     set_color,
#     set_behavior)

# assert num_threshold_pixels == surf.get_height() * surf.get_width()
# assert dest_surf.get_at((0,0)) == (40, 40, 40, 255)
