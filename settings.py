import pygame as pg

vec = pg.math.Vector2

WIDTH = 1024
HEIGHT = 768
TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)
LIGHTGRAY = (200, 200, 200)
BGCOLOR = (105, 50, 10)
CYAN = (0, 255, 255)

COLORS = [
    WHITE,
    BLACK,
    RED,
    YELLOW,
    CYAN,
    GREEN
]


WALL_IMG = 'tileGreen_39.png'
SOIL_IMG = 'tile_05.png'


# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [150, 120, 165, 75, 100]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
MOB_HEALTH = 100
AVOID_RADIUS = 50


BARREL_OFFSET = vec(10, 10)
KICKBACK = 100
GUN_SPREAD = 5
# Bullet settings
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
BULLET_DAMAGE = 10

PLAYER_SPEED = 500
PLAYER_ROT_SPEED = 250
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
PLAYER_HEALTH = 200


C_IMG = 'c.png'

HOUSE_IMG = 'medievalStructure_17.png'


DOOR_IMG = 'door.png'

FONT_NAME = 'fixedsys'


MODES = {
    'LYDIAN':[59, 60, 62, 64, 66, 67, 69, 71, 72],
    'AUGMENTED':[60, 62, 64, 66, 68, 70, 72],
    'DIMINISHED':[60, 63, 66, 69, 72],
    'FOURTHS':[55, 60, 65, 70, 75, 80],
}


PERSON_IMG = 'person.png'
