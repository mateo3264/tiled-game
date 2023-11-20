from settings import *
import pygame as pg
from random import uniform, choice
from tilemap import collide_hit_rect
from pygame import midi
import sys

vec = pg.math.Vector2

# sys.path.append('C:\\Users\\chave\\Estudio\\quote_mis_quote_proyectos\\pygame_pruebas')
sys.path.append('..')

from utils.patterns import PatternChecker2

from utils.draw_text import draw_speech_bubble



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
        self.pos = vec(x, y)
        self.rot = 0
        
        self.last_shot = 0

        self.health = PLAYER_HEALTH

        self.pattern_checker1 = PatternChecker2([60, 64, 67])
        self.pattern_checker2 = PatternChecker2([72, 77])
        self.pattern_checker3 = PatternChecker2([74, 76])
        self.pattern_checker4 = PatternChecker2([48, 55])
        

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
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game,  pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot) 
            
        
       
            
    
    def move(self, dx=0, dy=0):
        if not self.collide_with_walls(dx, dy):
            self.pos.x += dx
            self.pos.y += dy

    def piano_update(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)

        if self.game.midi_input.poll():
            midi_events = self.game.midi_input.read(15)
            midi2events = midi.midis2events(midi_events, 1)

            # dir, volume = self.pattern_checker1.check_pattern(midi2events, type='arpegios')
            shot = self.pattern_checker1.check_pattern(midi2events, type='chord')
            note_pattern_idx0 = self.pattern_checker2.check_pattern(midi2events, type='one-note', just_once=False)
            note_pattern_idx = self.pattern_checker3.check_pattern(midi2events, type='one-note', just_once=False)
            show_text = self.pattern_checker4.check_pattern(midi2events, type='chord')
            


            if shot:
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game,  pos, dir)


            if show_text:
                self.game.player_text = not self.game.player_text    
            
            # if dir == 'left': 
            #     print('left')
            #     self.rot_speed = PLAYER_ROT_SPEED
            # if dir == 'right': 
            #     print('right')
            #     self.rot_speed = -PLAYER_ROT_SPEED
            if note_pattern_idx0 == 0:
                self.rot_speed = PLAYER_ROT_SPEED
            if note_pattern_idx0 == 1:
                self.rot_speed = -PLAYER_ROT_SPEED

            if note_pattern_idx == 0:
                
                self.vel = vec(-PLAYER_SPEED, 0).rotate(-self.rot)
            if note_pattern_idx == 1:
                
                self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)


    def update(self):
        if self.game.playing_with_piano:
            self.piano_update()
        else:
            
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


        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.speed = choice(MOB_SPEEDS)

        self.rect.center = self.pos

        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center

        self.rot = 0   

        self.health = MOB_HEALTH 


        
    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif 30 < self.health <=60:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        if self.health < MOB_HEALTH:

            pg.draw.rect(self.image, col, (0, 0, width, 5))
    
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()





    def update(self):
        
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.zombie_img, self.rot)

        self.rect = self.image.get_rect()


        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + .5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

        
        self.rect.center = self.hit_rect.center

        if self.health <= 0:
            self.kill()


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image =  game.bullet_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        if now - self.spawn_time > BULLET_LIFETIME:
            self.kill()
        
        
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        hits = pg.sprite.spritecollideany(self, self.game.walls)

        if hits:
            self.kill()

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


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        
        #self.image = 
        #self.image.fill(GREEN)

        self.rect = pg.Rect(x, y, w, h)

        
        self.x = x
        self.y = y
        
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update(self):
        pass


class GrowingTree(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.growing_trees_group

        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.gid = 7
        self.image = self.game.map.tmxdata.get_tile_image_by_gid(self.gid)

        self.rect = self.image.get_rect()

        self.pos = vec(x, y)

        self.rect.center = self.pos

        self.last_update = 0

        self.time_to_change = 10000 
        self.time_to_change += choice([x for x in 
                                       range(-1 * (self.time_to_change - self.time_to_change // 2), 
                                             self.time_to_change + self.time_to_change // 2, self.time_to_change // 10
                                             )
                                        ]) 

        self.hit_rect = self.rect

    def update(self):
        now = pg.time.get_ticks()

        if now - self.last_update > self.time_to_change:
            for wall in enumerate(self.game.walls):
                        
                if isinstance(wall[1], Obstacle):
                    
                    if wall[1].x == self.pos.x and wall[1].y == self.pos.y:
                        print('kill!!')
                        wall[1].kill()
            if self.gid == 11:
                self.kill()
                return

            self.last_update = now
            self.gid += 1 
            center = self.rect.center
            self.image = self.game.map.tmxdata.get_tile_image_by_gid(self.gid)

            self.rect = self.image.get_rect()

            self.rect.center = self.pos


            
        
            # print(len(self.game.walls))
        
            if self.gid > 9:
                
                Obstacle(self.game, self.pos.x, self.pos.y,
                        self.game.map.tmxdata.width, self.game.map.tmxdata.height)


class House(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.houses

        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = self.game.house_img

        self.rect = self.image.get_rect()

        self.pos = vec(x, y)

        self.rect.center = self.pos

        self.hit_rect = self.rect

        Obstacle(self.game, self.pos.x, self.pos.y,
                 self.game.map.tmxdata.width,
                 self.game.map.tmxdata.height)
    
    def update(self):
        self.rect.center = self.pos