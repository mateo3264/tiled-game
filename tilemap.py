from settings import *
import pygame as pg
import pytmx

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

class Map:
    def __init__(self, filename):
        self.data = []

        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)

        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
    
    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        # pytmx.load_pygame(filename)
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    
                        
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight,))
                        
    def make_map(self):
        temp_surface = pg.Surface((self.width,
                                   self.height))
        self.render(temp_surface)

        return temp_surface



class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)

        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
    
    def update(self, target):
        x = -target.rect.centerx + WIDTH / 2
        y = -target.rect.centery + HEIGHT / 2

        x = min(0, x)
        y = min(0, y)

        x = max(x, -(self.width - WIDTH))
        y = max(y, -(self.height - HEIGHT))
        self.camera = pg.Rect(x, y, self.width, self.height) 
    

# def create_tilemap():
#     tmx_map = pytmx.TiledMap()
#     tmx_map.width = 50
#     tmx_map.height = 30
#     tmx_map.tilewidth = 64
#     tmx_map.tileheight = 64

#     tileset = pytmx.TiledTileset()
#     tileset.name = 'autotileset'
#     tileset.firstgid = 1
#     tileset.tilewidth = 64
#     tileset.tileheight = 64
#     tileset.spacing = 0
#     tileset.margin = 0

#     for i in range(1, 11):
#         tile = pytmx.TiledTile()
#         tile.id = i
#         tileset.add_tile(tile)#?????
    
#     tmx_map.add_tileset(tileset)


#     layer_data = [
#         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#         [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
#         # ... Add more rows as needed
#     ]

