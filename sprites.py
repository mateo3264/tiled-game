from settings import *
import pygame as pg
from tilemap import collide_hit_rect


vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.rect.width / 2
            elif sprite.vel.x <= 0:
                sprite.pos.x = hits[0].rect.right + sprite.rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x 
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.rect.height / 2
            elif sprite.vel.y <= 0:
                sprite.pos.y = hits[0].rect.bottom + sprite.rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y





class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = game.player_img

        

        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center

        
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)

        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            
        
       
            
    
    def move(self, dx=0, dy=0):
        if not self.collide_with_walls(dx, dy):
            self.pos.x += dx
            self.pos.y += dy

      
    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360

        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

        self.rect.center = self.hit_rect.center

        

        # self.rect.y = self.y * TILESIZE


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = game.zombie_img

        self.rect = self.image.get_rect()


        self.pos = vec(x, y) * TILESIZE
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.rect.center = self.pos

        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center

        self.rot = 0    
    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.zombie_img, self.rot)

        self.rect = self.image.get_rect()

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

        self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + .5 * self.acc * self.game.dt ** 2

        
        self.rect.center = self.hit_rect.center

    

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = game.wall_img#pg.Surface((TILESIZE, TILESIZE))
        #self.image = 
        #self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        
        self.x = x
        self.y = y
        
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
    
    def update(self):
        pass
