import sys

import os
import pygame as pg
from settings import *
from sprites import *
#from locations import *
from os import path
from tilemap import *
from pygame import midi
from midipatternspkg.draw_text import draw_image_bubble, draw_speech_bubble
from midipatternspkg.music_note_creation import create_seq_notes, RANGE_OF_NOTES

from automatic_house_creation import create_house_interior
import json
import re
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
        
        if self.playing_with_piano:
            
            self.midi_output = midi.Output(0)
            self.midi_output.set_instrument(1)
            

       

        

        self.player_text = False

        

        self.locations = json.load(open('locations.json', 'r', encoding='utf-8'))
        print('self.locations')
        print(self.locations)
        self.load_folders()
        self.generate_home_interiors()
        self.load_data()
        self.locations = json.load(open('locations.json', 'r', encoding='utf-8'))
        n_houses = 0
        for level, coords in self.locations['houses'].items():
            n_houses += len(coords)
        
        print('n_houses: ', n_houses)
        
        self.number_of_notes = 1
        
        json_filename = './snd/midi_notes.json'
        try:
            with open(json_filename, 'r', encoding='utf-8') as json_file:
                json_read = json.load(json_file)
                self.seq_notes = [midi_notes for idx, midi_notes in json_read.items()]
        except:
            #delete_score_images(self.snd_folder)
            self.seq_notes = [create_seq_notes(self.snd_folder, json_filename, self.number_of_notes, idx) for idx in range(n_houses)]
        print('self.seq_notes')
        print(self.seq_notes)
        self.range_of_notes = RANGE_OF_NOTES

        self.font_name = pg.font.match_font(FONT_NAME)   
    def load_audio_data(self):
        # todo: generalize not only to houses but to "places to enter"
        
        #self.midi_player = MidiPlayer(self)
        self.curr_midi_note_idx = 0
        self.curr_midi_note = None

        self.pickup_coin_snd = pg.mixer.Sound('Pickup_coin.wav')
        self.pickup_coin2_snd = pg.mixer.Sound('Pickup_coin2.wav')
        self.pickup_coin2_snd = pg.mixer.Sound('fruit1.wav')

    def load_folders(self):
        
        game_folder = path.dirname(__file__)
        self.img_folder = path.join(game_folder, 'img')
        self.snd_folder = path.join(game_folder, 'snd')

        self.map_folder = path.join(game_folder, 'maps')

    def load_data(self):

    
        self.map_info = {}
        idx = 1

        for file in os.listdir(self.map_folder):
            if '.tmx' in file:
                
                map = TiledMap(path.join(self.map_folder, file))
                map_img = map.make_map()
                map_rect = map_img.get_rect()
                d = {'map': map, 'map_img':map_img, 'map_rect':map_rect}
                
                self.map_info[file[:-4]] = d
                idx += 1

        print('self.map_info')
        print(self.map_info)


        self.player_img = pg.image.load(path.join(self.img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(self.img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.zombie_img = pg.image.load(path.join(self.img_folder, MOB_IMG)).convert_alpha()
        self.person_img = pg.image.load(path.join(self.img_folder, PERSON_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(self.img_folder, BULLET_IMG)).convert_alpha()
        self.c_note_img = pg.image.load(path.join(self.img_folder, C_IMG)).convert_alpha()
        self.house_img = pg.image.load(path.join(self.img_folder, HOUSE_IMG)).convert_alpha()
        self.door_img = pg.image.load(path.join(self.img_folder, DOOR_IMG)).convert_alpha()
        self.soil_img = pg.image.load(path.join(self.img_folder, SOIL_IMG)).convert_alpha()
        self.spritesheet = Spritesheet(path.join(self.img_folder, 'spritesheet_jumper.png'))
        self.spritesheet_chest = Spritesheet(path.join(self.img_folder, 'chest.png'))
        

    

    def generate_home_interiors(self):
        n_houses = 0
        for level, house_coors in self.locations['houses'].items():
            n_houses += len(house_coors)
        
        n_house_tmx_files = count_number_house_tmx_files(self.map_folder)

        while n_houses > n_house_tmx_files:
            create_house_interior()
            n_house_tmx_files = count_number_house_tmx_files(self.map_folder)

        
        

    def spawn_chests(self):
        print('self.current_level')
        print(self.current_level)
        print("self.locations['chests'][self.current_level]")
        print(self.locations['chests'][self.current_level])
        for i, (x, y) in enumerate(self.locations['chests'][self.current_level]):
            print('x,y', x, y)
            Chest(self, x, y, i)
    
    def delete_chests(self):
        for x, y in self.locations['chests'][self.current_level]:
            for chest in self.chests:
                if chest.pos.x == x and chest.pos.y == y:
                    chest.kill()

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
            House(self, *args, self.seq_notes[i], f'house_interior{i + 1}')
        
        print('house midi notes')
        print([house.midi_notes for house in self.houses])

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
        
        self.player = None
        for tile_obj in self.map_info[self.current_level]['map'].tmxdata.objects:
            if self.last_house_location is None:
                print('????')
                if tile_obj.name == 'player':
                
                    self.player = Player(self, tile_obj.x, tile_obj.y)
            elif self.last_house_location is not None and self.inside_house:
                self.inside_house = False
                print('not self.last_house_loction')
                self.player = Player(self, self.last_house_location[0], self.last_house_location[1] + 32)


            if tile_obj.name == 'wall':
                Obstacle(self, tile_obj.x, tile_obj.y,
                         tile_obj.width, tile_obj.height)
            
            elif tile_obj.name == 'good':
                
                GhostObstacle(self, tile_obj.x, tile_obj.y,
                         tile_obj.width, tile_obj.height, zone_type='good')
        
        if self.player is None:
            self.player = Player(self, 10, 10)
        spawn_mob_object(self, 100, 300)
        
        

        self.spawn_coins()

        self.spawn_chests()
        

        self.spawn_trees()
        
        self.spawn_houses()
        
        self.spawn_doors()

    def change_level(self, scene):
            
            print('self.curr_house')
            print(self.curr_house)
            self.player.kill()

            self.delete_trees()
            self.delete_houses()
            self.delete_doors()
            self.delete_coins()
            self.delete_chests()

            self.walls = pg.sprite.Group()
            self.current_level = scene
            
            self.spawn_level()


    def new(self):
        
        self.playing = True
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.ghost_walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.growing_trees_group = pg.sprite.Group()
        self.fruits = pg.sprite.Group()
        self.houses = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.chests = pg.sprite.Group()
        self.soils = pg.sprite.Group()

        
        

        self.number_of_coins_gained = 0


        self.number_of_fruits_gained = 0

        self.last_update = 0

        self.last_midi_update = 0

        self.level_idx = 0


        self.current_level = 'level1'

        self.curr_house = None

        self.last_house_location = None

        self.inside_house = False

    



        self.draw_score = False

        self.notes2enter_house = []

        
        
        
        self.camera = Camera(self.map_info['level1']['map'].width, self.map_info['level1']['map'].height)
        
        self.spawn_level()        

        self.create_canvas = True
        

        self.draw_debug = False

        self.load_audio_data()


        
        self.score_imgs = sorted([path.join(self.snd_folder, file) for file in os.listdir('./snd') if '.png' in file])
        print('self.score_imgs before')
        print(self.score_imgs)
        

        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

        self.score_imgs = sorted(self.score_imgs, key=natural_sort_key)        

        print('self.score_imgs after')
        print(self.score_imgs)
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
        if self.playing_with_piano:
            if self.midi_input.poll():
                midi_events = self.midi_input.read(15)
                self.midi2events = midi.midis2events(midi_events, 1)
        self.all_sprites.update()
        self.camera.update(self.player)
    
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)

        for hit in mob_hits:
            if not hit.is_healthy:
                self.player.health -= MOB_DAMAGE
                hit.vel = vec(0, 0)
                if self.player.health <= 0:
                    self.player.kill()
                    self.playing = False
        
        if mob_hits:
            if not hit.is_healthy:
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
            
            
            self.change_level('level1')

            self.last_house_location = None
        




    
    

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
        self.draw_text(f'Fruits: {self.number_of_fruits_gained}', 25, WHITE, WIDTH - 70, 80)

        draw_health_bar(self.screen, 20, 20, self.player.health / PLAYER_HEALTH)
        
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
