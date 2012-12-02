import kivy
kivy.require('1.4.1')
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.graphics import Line, Color, Ellipse, Rectangle, Point
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
import tmxlib
from kivy.core.image import Image
width, height = Window.size
# Window.clearcolor = (1, 1, 1, 1)


def set_zoom(lines, zoom=(48, 48), old_zoom=(48, 48)): #repopulates lists based on zoom level
    lat = range(0,width, zoom[0])
    long = range(0, height, zoom[1])
    lines = change_zoom(lines, zoom, old_zoom)
    return lat, long, lines
    
def change_zoom(lines, zoom, ozoom): # changes the size of all the lines to reflect zoom
    facx = zoom[0]/float(ozoom[1])
    facy = zoom[1]/float(ozoom[1])
    for line in range(len(lines)):
        points = (lines[line][0].points[0]*facx, lines[line][0].points[1]*facy, lines[line][0].points[2]*facx, lines[line][0].points[3]*facy)
        lines[line][0] = Line(points = points, width = 2)
    return lines
    
def snap_to(lines, zoom, lat): #uses the remainder between the point and the zoom to calculate where the point should snap to
    for line in lines:
        x = (line[0] % zoom[0]) - min(*lat)
        y = line[1] % zoom[1]
        if x >= zoom[0] / 2:
            x = -(zoom[0] - x)
        if y >= zoom[1] / 2:
            y = -(zoom[1] - y)
        line[0] = line[0] - x
        line[1] = line[1] - y
    return lines
def snap_image(pos, zoom, lat): # snaps an image to the top left of a box
    x = (pos[0] % zoom[0]) - min(*lat)
    y = pos[1] % zoom[1]
    pos[0] = pos[0] - x
    pos[1] = pos[1] - y
    return pos
    
def check_erase(pos, lines, drawn_lines): # checks to see if the eraser is colliding with any lines
    eraser = Widget(pos = pos, size = (height/18, height/18))
    for line in range(len(lines)):
        if (eraser.collide_point(lines[line][0].points[0], lines[line][0].points[1])
        or eraser.collide_point(lines[line][0].points[2], lines[line][0].points[3])):
            del lines[line]
            return
    for line in range(len(drawn_lines)):
        if (eraser.collide_point(drawn_lines[line][0].points[0], drawn_lines[line][0].points[1])
        or eraser.collide_point(drawn_lines[line][0].points[2], drawn_lines[line][0].points[3])):
            del drawn_lines[line]
            return

class Platform_draw(Widget):
    def color_change(self, instance): # function used to change the color of a line
        if instance.text == 'White':
            self.color = (1, 1, 1)
        elif instance.text == 'Red':
            self.color = (1, 0, 0)
        elif instance.text == 'Blue':
            self.color = (0, 0, 1)
        elif instance.text == 'Yellow':
            self.color = (1, 1, 0)
        elif instance.text == 'Green':
            self.color = (0, 0.7, 0)
        elif instance.text == 'Brown':
            self.color = (0.5, 0.25, 0.25)
            
    def undo(self, instance):  #removes the last line placed and then redraws the screen
        self.lines = self.lines[:-1]
        self.refresh_screen()
        
    def load(self, instance):
        self.map = tmxlib.Map.open(self.directory + '/' + 'test_old.tmx')
        self.old_zoom = self.zoom
        self.zoom = self.map.tile_size
        self.lat, self.long, self.lines = set_zoom(self.lines, self.zoom, self.old_zoom) # changes the size of all lines
        tile = self.map.tilesets[0][0].image.image # gets a random tile to access it values
        x_inc = 0
        y_inc = 0
        max_tiles = (tile.size[0] / float(self.zoom[0]))*(tile.size[1] / float(self.zoom[1])) # gets total tiles in image
        max_tiles = int(round(max_tiles))
        self.tileset = Image(self.directory + '/' + tile.source)
        for i in range(max_tiles):
            if y_inc >= tile.size[1]:
                x_inc += self.zoom[0] # adjust x and y for tile grab
                y_inc = 0
            texture = self.tileset.texture.get_region(x_inc, y_inc, self.zoom[0], self.zoom[1]) # creates texture from the tile at position x, y
            y_inc += self.zoom[1]
            self.tiles.append(texture) # adds to list of known tiles
        
        self.refresh_screen()
    def save(self, instance):
        self.map.save(self.directory + '/' + 'test.tmx')
    def save_load(self, instance):
        self.content = BoxLayout(orientation = 'vertical')
        savebtn = Button(text = 'Save')
        loadbtn = Button(text = 'Load')
        self.content.add_widget(savebtn)
        self.content.add_widget(loadbtn)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        self.popup = Popup(text = 'Save/Load', content = self.content, size_hint = (0.5, 0.2))
        self.popup.open()
        
    def toggle_straight(self, instance): #gets the line to snap to grid
        if self.old_x < width/4 and self.old_y > height/2:
            self.straight_type = 'single'
        else:
            self.straight_type = 'poly'
        self.refresh_screen()
        self.btnline.state = 'down'
    def select_type(self, instance): #for picking between single and poly lines
        self.canvas.add(Color(0, 0, 0, 0.6))
        self.canvas.add(Rectangle(size=(width, height)))
        self.canvas.add(Color(*self.color))
        self.canvas.add(Line(points=(width/4, height, width/4, height/2.4), width=1))
        self.canvas.add(Line(points=(0, height/2.4, width/4, height/2.4), width=1))
        
    def on_startup(self): #defines everything that needs to be defined before startup
        #defines variables to be used
        self.lines = []
        self.al = BoxLayout(orientation = 'vertical', size=(height/12, height), pos = (0, 0))
        self.ar = BoxLayout(orientation = 'vertical', size=(height/12, height), pos = (width-height/12, 0))
        self.coord = []
        self.drawn_lines = []
        self.straight_type = 'single'
        self.lat = ()
        self.long = ()
        self.zoom = (height/12, height/12)
        self.old_x = self.old_y = 0
        self.x = self.y = 0
        self.color = (1, 1, 1)
        self.tiles = []
        self.current_tile = 0
        self.tileset = []
        self.tile_list = []
        
        #creates all buttons used
        self.btnw = Button(text = 'White', size = self.zoom, size_hint = (None, None), background_color = (1, 1, 1, 0.8))
        self.btnr = Button(text = 'Red', size = self.zoom, size_hint = (None, None), background_color = (1, 0, 0, 0.8))
        self.btnb = Button(text = 'Blue', size = self.zoom, size_hint = (None, None), background_color = (0, 0, 1, 0.8))
        self.btny = Button(text = 'Yellow', size = self.zoom, size_hint = (None, None), background_color = (1, 1, 0, 0.8))
        self.btng = Button(text = 'Green', size = self.zoom, size_hint = (None, None), background_color = (0.2, 1, 0.2, 0.8))
        self.btnbr = Button(text = 'Brown', size = self.zoom, size_hint = (None, None), background_color = (1, 0.5, 0.5, 0.8))
        self.btnsave = Button(text = 'Save', size = self.zoom, size_hint = (None, None))
        self.btnline = ToggleButton(state = 'down', group = 'state', background_normal = 'images/line.png', background_down = 'images/lined.png', size = self.zoom, size_hint = (None, None))
        self.btnm = ToggleButton(group = 'state', background_normal = 'images/4_point.png', background_down = 'images/4_pointd.png', size = self.zoom, size_hint = (None, None))
        self.btnc = ToggleButton(group = 'state', background_normal = 'images/cursor.png', background_down = 'images/cursord.png', size = self.zoom, size_hint = (None, None))
        self.btndraw = ToggleButton(group = 'state', background_normal = 'images/draw.png',background_down = 'images/drawd.png', size = self.zoom, size_hint = (None, None))
        self.btntile = ToggleButton(group = 'state', text = 'tile', size = self.zoom, size_hint = (None, None))
        self.btnback = Button(background_normal = 'images/back.png', background_down = 'images/backd.png', size = self.zoom, size_hint = (None, None))
        
        #binds buttons to various functions
        self.btnw.bind(on_release = self.color_change)
        self.btnr.bind(on_release = self.color_change)
        self.btnb.bind(on_release = self.color_change)
        self.btny.bind(on_release = self.color_change)
        self.btng.bind(on_release = self.color_change)
        self.btnbr.bind(on_release = self.color_change)
        self.btnsave.bind(on_release = self.save_load)
        self.btnback.bind(on_release = self.undo)
        self.btnline.bind(on_release = self.toggle_straight)
        self.btnline.bind(on_press = self.select_type)
        
        self.ar.add_widget(self.btnw)
        self.ar.add_widget(self.btnr)
        self.ar.add_widget(self.btnb)
        self.ar.add_widget(self.btny)
        self.ar.add_widget(self.btng)
        self.ar.add_widget(self.btnbr)
        self.ar.add_widget(Widget())
        
        self.al.add_widget(self.btnsave)
        self.al.add_widget(self.btnline)
        self.al.add_widget(self.btnm)
        self.al.add_widget(self.btnc)
        self.al.add_widget(self.btndraw)
        self.al.add_widget(self.btntile)
        self.al.add_widget(self.btnback)
        self.al.add_widget(Widget())
        
        #refreshes screen ... just lateral lines
        self.lat, self.long, self.lines = set_zoom([], self.zoom)
        self.refresh_screen()
        
    def refresh_screen(self):
        self.canvas.clear()
        
        # draws tiles
        for tile in self.tile_list:
            self.canvas.add(tile)
              
        #draws grid lines
        for x in self.lat:
            self.canvas.add(Color(0, 0, 1))
            self.canvas.add(Line(points = (x, 0, x, height), width = 1))    
        for y in self.long:
            self.canvas.add(Color(0, 0, 1))
            self.canvas.add(Line(points = (0, y, width, y), width = 1))
            
        if min(*self.lat) < 0:
            self.lat[self.lat.index(min(*self.lat))] = max(*self.lat) + self.zoom[0]
        if max(*self.lat) > width:
            self.lat[self.lat.index(max(*self.lat))] = min(*self.lat) - self.zoom[0]

        #draws lines that the user has drawn
        for line in self.lines:
            self.canvas.add(Color(*line[1]))
            self.canvas.add(line[0])
        for line in self.drawn_lines:
            self.canvas.add(Color(*line[1]))
            self.canvas.add(line[0])
            
    def on_touch_down(self, touch): #defines the starting point of a new line
        if self.btnc.state == 'down':
            eraser = Ellipse(size = (height/18, height/18), pos=(touch.x-(height/36), touch.y-(height/36)))
            self.canvas.add(Color(1, 1, 1, 1))
            self.canvas.add(eraser)
            check_erase(eraser.pos, self.lines, self.drawn_lines)
        if self.btnline.state == 'down' or self.btntile.state == 'down':
            self.coord = [[touch.x, touch.y]]
        else: self.coord = []
        self.old_x, self.old_y = touch.x, touch.y
        
    def on_touch_up(self, touch):
        if self.x == 0 or self.y == 0 or [0,0] in self.coord:
            self.x, self.y = touch.x, touch.y #sets the start point of line
        if self.btntile.state == 'down' and len(self.tiles) > 0 and self.coord:
            pos = snap_image(self.coord[0], self.zoom, self.lat)
            tile  = Rectangle(texture = self.tiles[self.current_tile], pos = pos, size = self.zoom)
            self.tile_list.append(tile)
            self.coord = []
            self.refresh_screen()
            self.current_tile += 1
        if self.coord and self.btnline.state == 'down' and self.straight_type == 'single':
            self.coord.append([touch.x, touch.y]) #defines end point of new line
            self.coord = snap_to(self.coord, self.zoom, self.lat) #moves points onto grid
            if self.coord[0] == self.coord[1]:
                return
            line = [Line(points = (self.coord[0][0], self.coord[0][1], self.coord[1][0], self.coord[1][1]), width = 2), self.color]
            if not line in self.lines:
                self.lines.append(line)
            self.coord = []
            self.refresh_screen()
        self.old_x, self.old_y = touch.x, touch.y
        self.x = self.y = 0 # resets variables for finger lines
    def on_touch_move(self, touch):
        if self.btnc.state == 'down':
            self.refresh_screen()
            eraser = Ellipse(size = (height/18, height/18), pos=(touch.x-(height/36), touch.y-(height/36)))
            self.canvas.add(Color(1, 1, 1, 1))
            self.canvas.add(eraser)
            check_erase(eraser.pos, self.lines, self.drawn_lines)
        if self.btnline.state == 'down' or self.btndraw.state == 'down':
            if not self.coord:
                self.coord = [[touch.x, touch.y]] #used as a start point if finger just entered screen
            self.refresh_screen()
            self.canvas.add(Color(*self.color))
            coord_temp = [[self.x, self.y], [touch.x, touch.y]]
            if self.straight_type == 'single' and self.btnline.state == 'down':
                coord_temp[0] = self.coord[0]
                coord_temp = snap_to(coord_temp, self.zoom, self.lat)
            elif self.btnline.state == 'down':
                if self.x == 0 or self.y == 0 or [0,0] in self.coord:
                    self.x, self.y = touch.x, touch.y #sets the start point of line
                    return
                coord_temp = snap_to(coord_temp, self.zoom, self.lat)
                if coord_temp[0] == coord_temp[1]:
                    return
                line = [Line(points = (coord_temp[0][0], coord_temp[0][1], coord_temp[1][0], coord_temp[1][1]), width = 2), self.color]
                if not line in self.lines:
                    self.lines.append(line)
            line = Line(points = (coord_temp[0][0], coord_temp[0][1], coord_temp[1][0], coord_temp[1][1]), width = 1)  #draws a line that follows the users finger
            if self.btndraw.state == 'down':
                self.drawn_lines.append([line, self.color])
                self.coord = []
            self.canvas.add(line)
            self.x, self.y = touch.x, touch.y #updates points
             
        elif self.btnm.state == 'down':
            movex = touch.x - self.old_x
            for line in range(len(self.lines)):
                points = (self.lines[line][0].points[0] + movex, self.lines[line][0].points[1], self.lines[line][0].points[2] + movex, self.lines[line][0].points[3])
                self.lines[line][0] = Line(points = points, width = 2)
            for line in range(len(self.drawn_lines)):
                points = (self.drawn_lines[line][0].points[0] + movex, self.drawn_lines[line][0].points[1], self.drawn_lines[line][0].points[2] + movex, self.drawn_lines[line][0].points[3])
                self.drawn_lines[line][0] = Line(points = points, width = 1)
            for line in range(len(self.lat)):
                self.lat[line] += movex
            self.refresh_screen()
            self.old_x, self.old_y = touch.x, touch.y
            
            

class PlatformApp(App):
    title = ''
    icon = 'images/4_pointd.png'
    def settings(self, instance): # settings panel
        if instance.pos[0] == 0:
            self.btnal.pos = (self.zoom[0], height-self.zoom[1]*1.5)
            self.btnal.text = '<'
            self.parent.add_widget(self.main.al)
        elif instance.pos[0] == self.zoom[0]:
            self.btnal.pos = (0, height-self.zoom[1]*1.5)
            self.btnal.text = '>'
            self.parent.remove_widget(self.main.al)
            
    def color_choose(self, instance): # colours/tile panel
        if instance.pos[0] == width-self.zoom[0]/2:
            self.btnar.pos = (width-self.zoom[0]*1.5, height-self.zoom[1]*1.5)
            self.btnar.text = '>'
            self.parent.add_widget(self.main.ar)
        elif instance.pos[0] == width-self.zoom[0]*1.5:
            self.btnar.pos = (width-self.zoom[0]/2, height-self.zoom[1]*1.5)
            self.btnar.text = '<'
            self.parent.remove_widget(self.main.ar)
            
    def build(self):
        self.parent = Widget()
        self.main = Platform_draw()
        self.main.on_startup()
        self.main.lat, self.main.long, self.main.lines = set_zoom([], self.main.zoom)
        self.main.directory = self.directory
        self.main.upper = self
        self.zoom = self.main.zoom
        #adds the self.main class
        self.parent.add_widget(self.main)
        
        # creates buttons
        self.btnar = Button(text = '<', pos = (width-self.zoom[0]/2, height-self.zoom[1]*1.5), size=(self.zoom[0]/2, self.zoom[1]))
        self.btnal = Button(text = '>', pos = (0, height-self.zoom[1]*1.5), size=(self.zoom[0]/2, self.zoom[1]))
        
        self.btnal.bind(on_release = self.settings)
        self.btnar.bind(on_release = self.color_choose)
        
        # adds buttons to screen
        
        self.parent.add_widget(self.btnal)
        self.parent.add_widget(self.btnar)
       
        return self.parent
        
if __name__ in ('__android', '__main__'):
    PlatformApp().run()
