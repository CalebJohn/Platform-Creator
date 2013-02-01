import kivy
kivy.require('1.0.6')
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle


class Tileset(Widget):
    def __init__(self, name, width, height, source, zoom):
        super(Tileset, self).__init__()
        self.name = name
        self.width = int(width)
        self.height = int(height)
        self.source = source
        self.zoom = zoom
        self.image = Image(source)
        self.tiles = []
        self.max_tiles = (self.image.size[0] / float(width))*(self.image.size[1] / float(height)) # gets total tiles in image
        self.max_tiles = int(round(self.max_tiles))
        self.cut()
    def cut(self):
        x_inc = y_inc = 0
        for i in range(self.max_tiles):
            if y_inc >= self.image.size[1]:
                x_inc += self.width # adjust x and y for tile grab
                y_inc = 0
            texture = self.image.texture.get_region(x_inc, y_inc, self.width, self.height) # creates texture from the tile at position x, y
            y_inc += self.height
            self.tiles.append(Tile(texture, x_inc, y_inc, self.image.size[1], (self.width, self.height), self.zoom)) # adds to list of known tiles
        
    def tiles_list(self):
        for tile in self.tiles:
            yield tile
            
class Tile():
    def __init__(self, tile, x, y, height, size, zoom):
        self.tile = tile
        self.top_left = (x, height - y)
        self.size = (size[0]/ float(zoom[0]), size[1] / float(zoom[1]))