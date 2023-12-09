import sys

import os
import pygame as pg
from settings import *
from sprites import *
from locations import *
from os import path
from tilemap import *
from pygame import midi
from midipatternspkg.draw_text import draw_image_bubble, draw_speech_bubble
from midipatternspkg.music_note_creation import create_seq_notes, RANGE_OF_NOTES
# from utils.play_midi_notes import MidiPlayer
# from utils.spritesheet import Spritesheet


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

def delete_score_images(ruta):
    for file in os.listdir(ruta):
        os.remove(path.join(ruta, file))

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

       

        self.midi_output = midi.Output(2)

        self.player_text = False

        self.load_data()

        self.locations = LOCATIONS
        
        n_houses = 0
        for level, coords in self.locations['houses'].items():
            n_houses += len(coords)
        
        print('n_houses: ', n_houses)
        
        self.number_of_notes = 1
        delete_score_images(self.snd_folder)
        self.seq_notes = [create_seq_notes(self.snd_folder, 'midi_notes.txt', self.number_of_notes) for _ in range(n_houses)]

        self.range_of_notes = RANGE_OF_NOTES

        self.font_name = pg.font.match_font(FONT_NAME)   
    def load_audio_data(self):
        # todo: generalize not only to houses but to "places to enter"
        
        #self.midi_player = MidiPlayer(self)
        self.curr_midi_note_idx = 0
        self.curr_midi_note = None

        self.pickup_coin_snd = pg.mixer.Sound('Pickup_coin.wav')
        
    def load_data(self):
        
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.snd_folder = path.join(game_folder, 'snd')

        map_folder = path.join(game_folder, 'maps')
        self.map_info = []
        idx = 1

        for file in os.listdir(map_folder):
            if '.tmx' in file:
                map = TiledMap(path.join(map_folder, f'tiled{idx}.tmx'))
                map_img = map.make_map()
                map_rect = map_img.get_rect()
                d = {'map': map, 'map_img':map_img, 'map_rect':map_rect}
                self.map_info.append(d)
                idx += 1

        print('self.map_info')
        print(self.map_info)

        # self.map = TiledMap(path.join(map_folder, 'tiled1.tmx'))
        # self.map2 = TiledMap(path.join(map_folder, 'tiled2.tmx'))
        # self.map3 = TiledMap(path.join(map_folder, 'tiled3.tmx'))
        
        # self.current_map = self.map
        # #self.score = Spritesheet(path.join(img_folder, 'score1.png'))

        # self.map_img = self.map.make_map()
        
        # self.map2_img = self.map2.make_map()
        # self.map3_img = self.map3.make_map()
        # self.map_rect = self.map_img.get_rect()
        
        # self.map2_rect = self.map2_img.get_rect()
        # self.map3_rect = self.map3_img.get_rect()

        # self.map_list = [{'map':self.map, 'map_img':self.map_img, 'map_rect':self.map_rect}, 
        #              {'map':self.map2, 'map_img':self.map2_img, 'map_rect':self.map2_rect},
        #              {'map':self.map3, 'map_img':self.map3_img, 'map_rect':self.map3_rect},
        #             ]

        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.zombie_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.c_note_img = pg.image.load(path.join(img_folder, C_IMG)).convert_alpha()
        self.house_img = pg.image.load(path.join(img_folder, HOUSE_IMG)).convert_alpha()
        self.door_img = pg.image.load(path.join(img_folder, DOOR_IMG)).convert_alpha()
        self.spritesheet = Spritesheet(path.join(img_folder, 'spritesheet_jumper.png'))

    def spawn_coins(self):
        for x, y in self.locations['coins'][self.current_level]:
            Coin(self, x, y)
        
    def delete_coins(self):
        for x, y in self.locations['coins'][self.current_level]:
            for coin in self.coins:
                if coin.pos.x == x and coin.pos.y == y:
                    coin.kill()   

    def spawn_trees(self):
        for x, y in self.locations['trees'][self.current_level]:
            GrowingTree(self, x, y)
    
    def delete_trees(self):
        for x, y in self.locations['trees'][self.current_level]:
            for growing_tree in self.growing_trees_group:
                if growing_tree.pos.x == x and growing_tree.pos.y == y:
                    growing_tree.kill()
                    
        

    def spawn_houses(self):
        for i, args in enumerate(self.locations['houses'][self.current_level]):
            House(self, *args, self.seq_notes[i], i + 1)
    
    def delete_houses(self):
        for x, y in self.locations['houses'][self.current_level]:
            for house in self.houses:
                if house.pos.x == x and house.pos.y == y:
                    house.kill()
    
    def spawn_doors(self):
        
        for loc in self.locations['doors'][self.current_level]:
            Door(self, *loc)

    def delete_doors(self):
        for x, y in self.locations['doors'][self.current_level]:
            for door in self.doors:
                if door.pos.x == x and door.pos.y == y:
                    door.kill()

    def spawn_level(self):
        for tile_obj in self.map_info[self.current_level]['map'].tmxdata.objects:
            if tile_obj.name == 'player':
                self.player = Player(self, tile_obj.x, tile_obj.y)
            elif tile_obj.name == 'wall':
                Obstacle(self, tile_obj.x, tile_obj.y,
                         tile_obj.width, tile_obj.height)
        
        spawn_mob_object(self, 100, 300)
        
        self.spawn_coins()
        

        self.spawn_trees()
        
        self.spawn_houses()
        
        self.spawn_doors()

    def change_level(self, level):
            
            self.player.kill()

            self.delete_trees()
            self.delete_houses()
            self.delete_doors()
            self.delete_coins()
            self.walls = pg.sprite.Group()
            self.current_level = level
            
            self.spawn_level()


    def new(self):
        
        self.playing = True
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.growing_trees_group = pg.sprite.Group()
        self.houses = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        self.number_of_coins_gained = 0

        self.last_update = 0

        self.last_midi_update = 0

        self.level_idx = 0


        self.current_level = 0

        self.curr_house = None

    



        self.draw_score = False

        self.notes2enter_house = []

        
        
        
        self.camera = Camera(self.map_info[0]['map'].width, self.map_info[0]['map'].height)
        
        self.spawn_level()        

        self.create_canvas = True
        

        self.draw_debug = False

        self.load_audio_data()


        
        self.score_imgs = [path.join(self.snd_folder, file) for file in os.listdir('./snd') if '.png' in file]
        
        

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
                
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_t:
                    self.player_text = not self.player_text
                if event.key == pg.K_c:
                    #self.current_map_img = self.map2_img
                    
                    if self.create_canvas:
                        self.canvas = Canvas(self, 350, 150)
                    else:
                        self.canvas.kill()

                    self.create_canvas = not self.create_canvas
                        
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

        # house_hits = pg.sprite.spritecollide(self.player, self.houses, False, collide_hit_rect)

        # if house_hits:
        #     self.curr_house = house_hits[0]
        #     self.draw_score = True
        #     draw_image_bubble(self.screen, (500, 700), self.score_imgs[self.curr_house.scene - 1])
        # else:
        #     self.curr_house = None
        #     self.draw_score = False
        
        door_hits = pg.sprite.spritecollide(self.player, self.doors, False, collide_hit_rect)

        if door_hits:
            
            self.change_level(0)
        




    
    

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


    def draw(self):
        
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_info[self.current_level]['map_img'], self.camera.apply_rect(self.map_info[self.current_level]['map_rect']))
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
            draw_image_bubble(self.screen, (500, 700),  self.score_imgs[self.curr_house.scene - 1])
            
        self.draw_text(f'Coins: {self.number_of_coins_gained}', 25, WHITE, WIDTH - 70, 50)
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
