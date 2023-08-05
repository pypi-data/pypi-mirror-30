import os
from time import time
import pygame as pg
import pygame.examples as examples
from random import randint
import gc
screen_dims = [320, 200]


class Thingy(pg.sprite.DirtySprite):
    images = None
    def __init__(self):
        super(Thingy, self).__init__()
        self.image = Thingy.images[0]
        self.rect = list(self.image.get_rect())
        # self.rect = self.image.get_rect()
        # self.rect = [0, 0, 0, 0]
        self.rect[0] = randint(0, screen_dims[0])
        self.rect[1] = randint(0, screen_dims[1])
        #self.vel = [randint(-10, 10), randint(-10, 10)]
        self.vel = [randint(-1, 1), randint(-1, 1)]
        self.dirty = 2

    def update(self):
        for i in [0, 1]:
            nv = self.rect[i] + self.vel[i]
            if nv >= screen_dims[i] or nv < 0:
                self.vel[i] = -self.vel[i]
                nv = self.rect[i] + self.vel[i]
            self.rect[i] = nv

gc.disable()

def main():
    time_start = time()
    going = True
    frame_times = []
    frames = 0
    frames_since_last_gc = 0
    time_since_last_slow = 0
    rects = []
    pg.display.init()
    screen = pg.display.set_mode((320, 200))
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill([0, 0, 0])


    main_dir = os.path.split(os.path.abspath(examples.__file__))[0]
    data_dir = os.path.join(main_dir, 'data')
    sprite_surface = pg.image.load(os.path.join(data_dir, "asprite.bmp"))
    sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], pg.SRCCOLORKEY|pg.RLEACCEL)
    Thingy.images = [sprite_surface]
    sprites = pg.sprite.LayeredDirty()
    for i in range(100):
        sprites.add(Thingy())


    while going:
        time_top = time()

        # for e in pg.event.get():
        #     if e.type == pg.QUIT:going = False
        #     if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:going = False


        # sprites.clear(screen, background)
        # sprites.update()
        # rects = sprites.draw(screen)
        [pg.Rect(0,0,0,0) for x in range(100)]


        time_bottom = time()
        # print (time_bottom - time_top)
        if time_bottom - time_top > 0.011:
            print ('+%s, %s' % (time_bottom - time_top, time_bottom - time_since_last_slow))
            time_since_last_slow = time_bottom
        if time_bottom - time_top < 0.005:
            pass
            # print ('----%s' % (time_bottom - time_top))
        pg.display.update(rects)
        time_after_flip = time()

    pg.quit()

if __name__ == '__main__':
    main()