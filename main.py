import pygame as pg
from settings import *
from sprites import *
from os import path
from tilemap import *
from pygame import midi
from utils.draw_text import draw_image_bubble, draw_speech_bubble
from utils.music_note_creation import create_seq_notes, RANGE_OF_NOTES
from utils.play_midi_notes import MidiPlayer
from utils.spritesheet import Spritesheet

midi.init()

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


def spawn_scene_object(game, gid, x, y):
    

    soil_tile = game.map.tmxdata.get_tile_image_by_gid(1)
    game.map_img.blit(soil_tile, (x, y))

    tile = game.map.tmxdata.get_tile_image_by_gid(gid)
    game.map_img.blit(tile, (x, y))
    for wall in game.walls:
        if isinstance(wall, Obstacle):
            if wall.x == x and wall.y == y:
                wall.kill()
    if gid > 9:
        
        Obstacle(game, x, y,
                game.map.tmxdata.width, game.map.tmxdata.height)




#TODO: ensure it doesn't spawn in a place where it shouldn't (like above a tree)
def spawn_mob_object(game, x, y):
    Mob(game, x, y)

class Game:
    def __init__(self):
        self.running = True
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()

        #pg.key.set_repeat(100)
        try:
            self.midi_input = midi.Input(1)
            self.playing_with_piano = True
        except:
            self.playing_with_piano = False

        print('self.playing_with_piano')
        print(self.playing_with_piano)

        self.midi_output = midi.Output(2)

        self.player_text = False

        self.load_data()

        self.range_of_notes = RANGE_OF_NOTES
    def load_audio_data(self):
        
        self.midi_notes = create_seq_notes()
        self.midi_player = MidiPlayer(self)
        self.curr_midi_note_idx = 0
        self.curr_midi_note = self.midi_notes[self.curr_midi_note_idx]
        
    def load_data(self):
        
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        map_folder = path.join(game_folder, 'maps')
        self.map = TiledMap(path.join(map_folder, 'tiled1.tmx'))
        self.map2 = TiledMap(path.join(map_folder, 'tiled2.tmx'))

        self.score = Spritesheet(path.join(img_folder, 'score1.png'))

        self.map_img = self.map.make_map()
        self.current_map_img = self.map_img
        self.map2_img = self.map2.make_map()
        self.map_rect = self.map_img.get_rect()
        self.map2_rect = self.map2_img.get_rect()

        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.zombie_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.c_note_img = pg.image.load(path.join(img_folder, C_IMG)).convert_alpha()
        self.house_img = pg.image.load(path.join(img_folder, HOUSE_IMG)).convert_alpha()
        print(self.map)


    def new(self):
        self.playing = True
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.growing_trees_group = pg.sprite.Group()
        self.houses = pg.sprite.Group()

        self.last_update = 0

        self.last_midi_update = 0

        self.growing_trees = [(100, 100), (150, 100), (100, 150), (150, 150)]

        for x, y in self.growing_trees:
            GrowingTree(self, x, y)

        House(self, 400, 300)

        self.draw_score = False

        self.notes2enter_house = []

        for tile_obj in self.map.tmxdata.objects:
            if tile_obj.name == 'player':
                self.player = Player(self, tile_obj.x, tile_obj.y)
            elif tile_obj.name == 'wall':
                Obstacle(self, tile_obj.x, tile_obj.y,
                         tile_obj.width, tile_obj.height)
        
        
        spawn_mob_object(self, 100, 300)
        self.camera = Camera(self.map.width, self.map.height)
        
        self.canvas = Canvas(self, 350, 350)

        

        self.draw_debug = False

        self.load_audio_data()
        self.midi_idx = 0

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
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_t:
                    self.player_text = not self.player_text
                if event.key == pg.K_c:
                    self.current_map_img = self.map2_img
                # if event.key == pg.K_i:
                #     ImageBubble(self)

    
    def update(self):
        #self.curr_midi_note = self.midi_player.play_midi_note()
        
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

        hit_houses = pg.sprite.spritecollide(self.player, self.houses, False, collide_hit_rect)

        if hit_houses:
            self.draw_score = True
            draw_image_bubble(self.screen, (500, 700))
        else:
            self.draw_score = False



    
    
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (0, y), (WIDTH, y))

    def draw(self):
        
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.current_map_img, self.camera.apply_rect(self.map_rect))
        draw_health_bar(self.screen, 20, 20, self.player.health / PLAYER_HEALTH)
        # self.draw_grid()
        # self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))

            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)

        if self.player_text:
            draw_speech_bubble(self.screen, 'Hi!!!', BLACK, WHITE, 
                               (20, 20), 20
                               )
        if self.draw_score:
            draw_image_bubble(self.screen, (500, 700))
            
        # score = self.score.get_image(0, 0, 350, 120)
        # self.screen.blit(score, (200, 0))
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
