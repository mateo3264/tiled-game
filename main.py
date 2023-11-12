import pygame as pg
from settings import *
from sprites import *
from os import path
from tilemap import *


def draw_health_bar(surf, x, y, pct):
        if pct > .7:
            col = GREEN
        elif .4 < pct <= .7:
            col = YELLOW
        else:
            col = RED
        width = int(PLAYER_HEALTH * pct)
        pg.draw.rect(surf, col, (20, 20, width, 15)) 
        pg.draw.rect(surf, WHITE, (20, 20, PLAYER_HEALTH, 15), 2) 

class Game:
    def __init__(self):
        self.running = True
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()

        pg.key.set_repeat(100)

        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        map_folder = path.join(game_folder, 'maps')
        self.map = TiledMap(path.join(map_folder, 'tiled1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.zombie_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        print(self.map)


    def new(self):
        self.playing = True
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()

        
        # for y, tiles in enumerate(self.map.data):
        #     for x, tile in enumerate(tiles):
        #         if tile == '1':
        #             Wall(self, x, y)
        #         if tile == 'P':
        #             self.player = Player(self, x, y)
                
        #         if tile == 'M':
        #             Mob(self, x, y)
        self.player = Player(self, 5, 5)
        self.camera = Camera(self.map.width, self.map.height)

        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
        
    
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    print('space')

    
    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
    
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)

        for hit in mob_hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.player.kill()
                self.playing = False
        
        if mob_hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0 ).rotate(-mob_hits[0].rot)
        
        bullet_hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)

        for hit in bullet_hits:
            hit.health -= BULLET_DAMAGE 
            hit.vel = vec(0, 0)
            
    
    
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        draw_health_bar(self.screen, 20, 20, self.player.health / PLAYER_HEALTH)
        # self.draw_grid()
        # self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()
    
    def show_start_screen(self):
        pass
    def show_go_screen(self):
        pass

g = Game()
g.show_start_screen()

while g.running:
    g.new()
    g.show_go_screen()
