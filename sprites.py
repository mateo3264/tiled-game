from settings import *
import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.Surface((TILESIZE, TILESIZE))

        self.image.fill(YELLOW)

        self.rect = self.image.get_rect()

        self.x = x
        self.y = y
    
    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy
    
    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.Surface((TILESIZE, TILESIZE))

        self.image.fill(GREEN)

        self.rect = self.image.get_rect()

        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
    
    def update(self):
        pass
