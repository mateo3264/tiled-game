import pygame as pg
from settings import *
from sprites import *

class Game:
    def __init__(self):
        self.running = True
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()

        pg.key.set_repeat(50)

        self.load_data()

    def load_data(self):
        pass 

    def new(self):
        self.playing = True
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        self.player = Player(self, 0, 0)
        for i in range(5, 10):
            Wall(self, i, 5)
        while self.playing:
            self.events()
            self.update()
            self.draw()
        
        self.run()
    
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    print('space')
                if event.key == pg.K_LEFT:
                    self.player.move(dx=-1)
                if event.key == pg.K_RIGHT:
                    self.player.move(dx=1)
                if event.key == pg.K_UP:
                    self.player.move(dy=-1)
                if event.key == pg.K_DOWN:
                    self.player.move(dy=1)
    
    def update(self):
        self.all_sprites.update()
    
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(GRAY)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
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
