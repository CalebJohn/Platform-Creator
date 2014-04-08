import kivy
kivy.require('1.0.6')
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.app import App
from kivy.config import ConfigParser
from kivy.graphics import Line, Color, Ellipse, Rectangle, Rotate
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from extras import Drawable, Polyline

width, height = Window.size
# Window.clearcolor = (1, 1, 1, 1)

def set_zoom(lines, zoom=(50, 50), old_zoom=(50, 50), lat=None, longit=None): #repopulates lists based on zoom level
    if lat != None and longit != None:
        offx = float(min(*lat))
        offy = float(min(*longit))
    else:
        offx = 0
        offy = 0
    lat = range(0, width, zoom[0])
    longit = range(0, height, zoom[1])
    lines = change_zoom(lines, zoom, old_zoom, offx, offy)
    return lat, longit, lines
    
def change_zoom(lines, zoom, ozoom, offx, offy): # changes the size of all the lines to reflect zoom
    for line in lines:
        line.translate(zoom, ozoom, offx, offy)
    return lines
    
def check_erase(eraser, lines, zoom, lat, longit): # checks to see if the eraser is colliding with any lines
    for line in lines:
        if line.collide(eraser):
            del lines[lines.index(line)]
            
def color_change(color, pos):
    step = 0.1
    if pos == 2:
        if color[0] > 0.0:
            color = (color[0] - step, 0.0, 1.0)
        elif color[1] < 1.0:
            color = (0.0, color[1] + step, 1.0)
        else:
            pos = 1
            color = (0.0, 1.0, 1.0)
    if pos == 1:
        if color[2] > 0.0:
            color = (0.0, 1.0, color[2] - step)
        elif color[0] < 1.0:
            color = (color[0] + step, 1.0, 0.0)
        else:
            pos = 0
            color = (1.0, 1.0, 0.0)
    if pos == 0:
        if color[1] > 0.0:
            color = (1.0, color[1] - step, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
    return color, pos
        
            
def color_load():
    colors = [(0.5, 0.25, 0.25)]
    color = (1.0, 0.0, 1.0)
    pos = 2
    for i in range(1000):
        color, pos = color_change(color, pos)
        colors.append(color)
        if color == (1.0, 1.0, 1.0):
            break
    return colors

def get_directory(source):
    b = source.split('\\')
    if len(source) == 1:
        b = source.split('/')
    b = b[-1]
    return source[:-len(b)]
    
# breaks the data into a savable format
def Save(zoom, lines):
    with open("saved.lines", "w") as savefile:
        savefile.write(str(zoom) + "\n")
        for line in lines:
            savefile.write(str(line.save()) + "\n")
    
# Parses a save file and return its contents
def Load():
    lines = []
    zoom = 0
    with open("saved.lines", "r") as loadfile:
        zoom = eval(loadfile.readline())
        for line in loadfile.readlines():
            l = eval(line)
            # polyline
            if type(l) == list:
                p = Polyline()
                p.load(l)
                lines.append(p)
            # regular line
            else:
                lines.append(Drawable(Line, **l))
    return zoom, lines

    
class UI(Widget):
    def value_change(self, instance, touch): # the function for showing color change on slider
        if touch.x < instance.pos[0]:
            return
        self.grid.color = self.grid.colors[int(instance.value)]
        self.canvas.add(Color(*self.grid.color))
        self.canvas.add(Rectangle(size = (width/2, height/2), pos = (0, height/4)))
        self.add_widget(Label(text = str(int(instance.value)), color = (0, 0, 0, 1), font_size=height/12, pos = (height/12, height/2)))
        self.grid.coord = []
        self.grid.x = self.grid.y = 0
    
    def value_zoom(self, instance, touch):
        if touch.y > height-height/12:
            old_zoom = self.grid.zoom
            self.grid.zoom = (int(instance.value), int(instance.value))
            self.grid.lat, self.grid.longit, self.grid.lines = set_zoom(self.grid.lines, self.grid.zoom, old_zoom, self.grid.lat, self.grid.longit) # changes the size of all lines
            self.grid.coord = []
            self.grid.x = self.grid.y = 0
            self.grid.refresh_screen()
            
    def create_view(self, message):
        view = ModalView(size_hint=(0.15, 0.05))
        view.add_widget(Label(text = message))
        view.open()
        
    def load(self, instance):
        self.grid.load()
        self.popup.dismiss()
    
    def save(self, instance):
        self.grid.save()
        self.popup.dismiss()
        
    def save_load(self, instance):
        content = BoxLayout(orientation = 'vertical')
        savebtn = Button(text = 'Save')
        loadbtn = Button(text = 'Load')
        content.add_widget(savebtn)
        content.add_widget(loadbtn)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        self.popup = Popup(title = 'Menu', content = content, size_hint = (0.5, 0.3))
        self.popup.open()
        
    def toggle_straight(self, instance): #gets the line to snap to grid
        if self.grid.old_x < width/4 and self.grid.old_y > height/2:
            self.grid.straight_type = 'single'
        else:
            self.grid.straight_type = 'poly'
        self.canvas.clear()
        self.btnline.state = 'down'
    def select_type(self, instance): #for picking between single and poly lines
        self.canvas.add(Color(0, 0, 0, 0.6))
        self.canvas.add(Rectangle(size=(width, height)))
        self.canvas.add(Color(*self.grid.color))
        self.canvas.add(Line(points=(width/4, height, width/4, height/2.4), width=1))
        self.canvas.add(Line(points=(0, height/2.4, width/4, height/2.4), width=1))
        
    def clear(self, *args):
        self.canvas.clear()
    
    def on_startup(self): #defines everything that needs to be defined before startup
        #defines variables to be used
        self.al = BoxLayout(orientation = 'vertical', size=(height/12, height), pos = (0, 0))
        self.ac = BoxLayout(orientation = 'vertical')
        self.at = BoxLayout(orientation = 'vertical')
        self.ar = BoxLayout(orientation = 'vertical', size=(height/12, height), pos = (width-height/12, 0))
        self.straight_type = 'single'
        self.size = (height/12, height/12)
        
        #creates all buttons used
        self.btnmenu = Button(text = 'Menu', size = self.size, size_hint = (None, None))
        self.btnline = ToggleButton(state = 'down', group = 'state', background_normal = 'images/line.png', background_down = 'images/lined.png', size = self.size, size_hint = (None, None))
        self.btnm = ToggleButton(group = 'state', background_normal = 'images/4_point.png', background_down = 'images/4_pointd.png', size = self.size, size_hint = (None, None))
        self.btnc = ToggleButton(group = 'state', background_normal = 'images/cursor.png', background_down = 'images/cursord.png', size = self.size, size_hint = (None, None))
        self.btndraw = ToggleButton(group = 'state', background_normal = 'images/draw.png', background_down = 'images/drawd.png', size = self.size, size_hint = (None, None))

        self.btnback = Button(background_normal = 'images/back.png', background_down = 'images/backd.png', size = self.size, size_hint = (None, None))
        self.btnsettings = Button(background_normal = 'images/gear.png', background_down = 'images/geard.png', size = self.size, size_hint = (None, None))
        self.color_slider = Slider(orientation = 'vertical', max = len(self.grid.colors)-1, min = 0, size_hint = (1, None), step = 1, height = height-40, value = len(self.grid.colors)-1)
        
        
        #binds buttons to various functions
        self.btnmenu.bind(on_release = self.save_load)
        self.btnback.bind(on_release = self.grid.undo)
        self.btnline.bind(on_release = self.toggle_straight)
        self.btnline.bind(on_press = self.select_type)
        self.btnsettings.bind(on_release = self.upper.open_settings)
        self.color_slider.bind(on_touch_move = self.value_change)
        self.color_slider.bind(on_touch_up = self.clear)
        
        self.ac.add_widget(Widget(height=20))
        self.ac.add_widget(self.color_slider)
        self.ac.add_widget(Widget())
        
        self.at.add_widget(Widget(height=20))
        self.at.add_widget(Widget())
        
        self.ar.add_widget(self.ac)
        
        self.al.add_widget(self.btnmenu)
        self.al.add_widget(self.btnline)
        self.al.add_widget(self.btnm)
        self.al.add_widget(self.btnc)
        self.al.add_widget(self.btndraw)
        self.al.add_widget(self.btnback)
        self.al.add_widget(Widget())
        self.al.add_widget(self.btnsettings)
        
    
class Platform_draw(Widget):

    def undo(self, instance):  #removes the last line placed and then redraws the screen
        self.lines = self.lines[:-1]
        self.refresh_screen()
        
    def on_startup(self): #defines everything that needs to be defined before startup
        #defines variables to be used
        self.lines = []
        self.coord = []
        # drawn lines is what your fingure is tracing, disappears on touch up
        self.drawn_lines = []
        self.polyline = None
        self.straight_type = 'single'
        self.lat = ()
        self.longit = ()
        self.old_x = self.old_y = 0
        self.x = self.y = 0
        self.size = (height/12, height/12)
        self.colors = color_load()
        self.color = self.colors[-1]
        self.currentLayer = 0
        
        #refreshes screen ... just lateral lines
        self.lat, self.longit, self.lines = set_zoom([], self.zoom)
        self.refresh_screen()
    
    def save(self):
        Save(self.zoom, self.lines)
    
    def load(self):
        self.zoom, self.lines = Load()
        self.lat, self.longit, self.lines = set_zoom(self.lines, self.zoom, self.zoom, self.lat, self.longit) # changes the size of all lines
        self.coord = []
        self.x = self.y = 0
        setattr(self.zoom_slider, 'value' ,self.zoom[0])
        self.refresh_screen()
    
    def refresh_screen(self):
        self.canvas.clear()
              
        #draws grid lines
        for x in self.lat:
            self.canvas.add(Color(*self.gridColor))
            self.canvas.add(Line(points = (x, 0, x, height), width = 1))    
        for y in self.longit:
            self.canvas.add(Color(*self.gridColor))
            self.canvas.add(Line(points = (0, y, width, y), width = 1))

        #draws lines that the user has drawn
        for line in self.lines:
            line.draw(self.canvas)
            # self.canvas.add(Color(*line[1]))
            # self.canvas.add(line[0])
            
        for line in self.drawn_lines:
            self.canvas.add(Color(*line[1]))
            self.canvas.add(line[0])
            
        with self.canvas:
            Color(0.2, 0.2, 0.2)
            Rectangle(pos = (0, height-height/12), size = (width, self.size[1]))
            if len(self.upper.parent.children) > 0:
                if self.upper.btnar.pos[0] == width-self.size[0]*1.5:
                    Rectangle(pos = (width-self.size[0], 0), size = (self.size[0], height))
            
    def on_touch_down(self, touch): #defines the starting point of a new line
        if self.ui.btnc.state == 'down':
            eraser = Drawable(Rectangle, size = self.zoom, pos=(touch.x, touch.y), color = (1, 1, 1, 0.5))
            eraser.snap(list(eraser.item.pos), self.zoom, self.lat, self.longit)
            eraser.draw(self.canvas)
            check_erase(eraser, self.lines, self.zoom, self.lat, self.longit)
            self.refresh_screen()
        if self.ui.btnline.state == 'down':
            self.coord = [[touch.x, touch.y]]

        if self.ui.btndraw.state == 'down':
            self.polyline = Polyline(self.color)
        else: self.coord = []
        self.old_x, self.old_y = touch.x, touch.y
        
    def on_touch_up(self, touch):
        if self.x == 0 or self.y == 0 or [0, 0] in self.coord:
            self.x, self.y = touch.x, touch.y #sets the start point of line
        if self.coord and self.ui.btnline.state == 'down' and self.straight_type == 'single' and touch.y < height-height/12:
            self.coord.append([touch.x, touch.y]) #defines end point of new line
            line = Drawable(Line, color = self.color, points = (self.coord[0][0], self.coord[0][1], self.coord[1][0], self.coord[1][1]), width = 2)
            if not line.snap(self.coord, self.zoom, self.lat, self.longit):
                return
            if not line in self.lines:
                self.lines.append(line)
            self.coord = []
            self.refresh_screen()
        if self.ui.btndraw.state == 'down' and self.polyline != None:
            self.lines.append(self.polyline)
            self.polyline = None
            self.coord = []
            self.drawn_lines = []
            self.refresh_screen()
        self.old_x, self.old_y = touch.x, touch.y
        self.x = self.y = 0 # resets variables for finger lines
    def on_touch_move(self, touch):
        if self.x == 0 or self.y == 0 or [0, 0] in self.coord:
            self.x, self.y = touch.x, touch.y #sets the start point of line
        if self.ui.btnc.state == 'down':
            self.refresh_screen()
            eraser = Drawable(Rectangle, size = self.zoom, pos=(touch.x, touch.y), color = (1, 1, 1, 0.5))
            eraser.snap(list(eraser.item.pos), self.zoom, self.lat, self.longit)
            eraser.draw(self.canvas)
            check_erase(eraser, self.lines, self.zoom, self.lat, self.longit)
        if self.ui.btnline.state == 'down' or self.ui.btndraw.state == 'down' and touch.y < height-height/12:
            if not self.coord:
                self.coord = [[touch.x, touch.y]] #used as a start point if finger just entered screen
            self.refresh_screen()
            self.canvas.add(Color(*self.color))
            coord_temp = [[self.x, self.y], [touch.x, touch.y]]
            if self.straight_type == 'single' and self.ui.btnline.state == 'down':
                coord_temp[0] = self.coord[0]
                line = Drawable(Line, color = self.color, points = (coord_temp[0][0], coord_temp[0][1], coord_temp[1][0], coord_temp[1][1]), width = 1)
                line.snap(coord_temp, self.zoom, self.lat, self.longit)
                line.draw(self.canvas)
            elif self.ui.btnline.state == 'down':
                if self.x == 0 or self.y == 0 or [0, 0] in self.coord:
                    self.x, self.y = touch.x, touch.y #sets the start point of line
                    return
                line = Drawable(Line, color = self.color, points = (coord_temp[0][0], coord_temp[0][1], coord_temp[1][0], coord_temp[1][1]), width = 2)
                if not line.snap(coord_temp, self.zoom, self.lat, self.longit):
                    return
                if not line in self.lines:
                    self.lines.append(line)
            if self.ui.btndraw.state == 'down' and self.polyline != None:
                self.polyline.add_line(coord_temp[0][0], coord_temp[0][1], coord_temp[1][0], coord_temp[1][1])
                self.drawn_lines.append([Line(points = (coord_temp[0][0], coord_temp[0][1], coord_temp[1][0], coord_temp[1][1])), self.color])
            self.x, self.y = touch.x, touch.y #updates points
             
        if self.ui.btnm.state == 'down':
            if touch.x > width - height/12 or touch.y > height-height/12:
                return
            movex = touch.x - self.old_x
            movey = touch.y - self.old_y
            for line in self.lines:
                line.move(movex, movey)
            for line in range(len(self.drawn_lines)):
                points = (self.drawn_lines[line][0].points[0] + movex, self.drawn_lines[line][0].points[1] + movey, self.drawn_lines[line][0].points[2] + movex, self.drawn_lines[line][0].points[3] + movey)
                self.drawn_lines[line][0] = Line(points = points, width = 1)
            for line in range(len(self.lat)):
                self.lat[line] += movex
            for line in range(len(self.longit)):
                self.longit[line] += movey
            self.refresh_screen()
            self.old_x, self.old_y = touch.x, touch.y
            
            # ensures that their are always grid lines on the screen
            while min(*self.lat) < 0:
                self.lat[self.lat.index(min(*self.lat))] = max(*self.lat) + self.zoom[0]
            while max(*self.lat) > width:
                self.lat[self.lat.index(max(*self.lat))] = min(*self.lat) - self.zoom[0]
            while min(*self.longit) < 0:
                self.longit[self.longit.index(min(*self.longit))] = max(*self.longit) + self.zoom[0]
            while max(*self.longit) > height:
                self.longit[self.longit.index(max(*self.longit))] = min(*self.longit) - self.zoom[0]
            
            

class PlatformApp(App):
    title = ''
    icon = 'images/4_pointd.png'
    use_kivy_settings = False
    def settings(self, instance): # settings panel
        if instance.pos[0] == 0:
            self.btnal.pos = (self.zoom[0], height-self.zoom[1]*1.5)
            self.btnal.text = '<'
            self.parent.add_widget(self.ui.al)
            
        elif instance.pos[0] == self.zoom[0]:
            self.btnal.pos = (0, height-self.zoom[1]*1.5)
            self.btnal.text = '>'
            self.parent.remove_widget(self.ui.al)
        
    def color_choose(self, instance): # colours/tile panel
        if instance.pos[0] == width-self.zoom[0]/2:
            self.btnar.pos = (width-self.zoom[0]*1.5, height-self.zoom[1]*1.5)
            self.btnar.text = '>'
            self.parent.add_widget(self.ui.ar)
            
        elif instance.pos[0] == width-self.zoom[0]*1.5:
            self.btnar.pos = (width-self.zoom[0]/2, height-self.zoom[1]*1.5)
            self.btnar.text = '<'
            self.parent.remove_widget(self.ui.ar)
            
        self.ui.ar.clear_widgets()

        self.ui.ar.add_widget(self.ui.ac)
        
        self.grid.refresh_screen()
            
    def build(self):
        self.config = ConfigParser()
        self.config.read(self.directory + '/' + 'config.ini')
        self.parent = Widget()
        self.parent.canvas.clear()
        self.parent.canvas.add(Color(0, 0, 0))
        self.parent.canvas.add(Rectangle(size=(width, height)))
        self.grid = Platform_draw()
        self.ui = UI()
        self.grid.ui = self.ui
        self.ui.grid = self.grid
        
        try: 
            zoom = int(self.config.get('platform', 'zoom'))
            self.grid.zoom = (zoom, zoom)
        except:
            self.grid.zoom = (height/12, height/12)
        try:
            gridR = int(self.config.get('colors', 'r'))
        except:
            gridR = 0
        try:
            gridG = int(self.config.get('colors', 'g'))
        except:
            gridG = 0
        try:
            gridB = int(self.config.get('colors', 'b'))
        except:
            gridB = 1
        
        self.grid.gridColor = (gridR/255.0, gridG/255.0, gridB/255.0)
        self.grid.directory = self.directory
        self.grid.upper = self
        self.ui.upper = self
        self.grid.on_startup()
        self.ui.on_startup()
        self.grid.lat, self.grid.longit, self.grid.lines = set_zoom([], self.grid.zoom)
        self.zoom = self.grid.size
        #adds the main classes
        self.parent.add_widget(self.grid)
        self.parent.add_widget(self.ui)
        
        # creates buttons
        self.btnar = Button(text = '<', pos = (width-self.zoom[0]/2, height-self.zoom[1]*1.5), size=(self.zoom[0]/2, self.zoom[1]))
        self.btnal = Button(text = '>', pos = (0, height-self.zoom[1]*1.5), size=(self.zoom[0]/2, self.zoom[1]))
        self.zoom_slider = Slider(orientation = 'horizontal', size = (width - height/3, height/12), pos = (height/6, height-height/12), max = height/6, min = 20, value = self.zoom[1], step = 1)
        
        # gives grid a referance to the zoom slider, (for loading)
        self.grid.zoom_slider = self.zoom_slider
        
        self.btnal.bind(on_release = self.settings)
        self.btnar.bind(on_release = self.color_choose)
        self.zoom_slider.bind(on_touch_move = self.ui.value_zoom)
        
        # adds buttons to screen
        
        self.parent.add_widget(self.btnal)
        self.parent.add_widget(self.btnar)
        self.parent.add_widget(self.zoom_slider)
       
        return self.parent
    def build_settings(self, settings):
        settings.add_json_panel('Defaults', self.config, self.directory + '/' + 'settings.json')
    
    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('platform', 'zoom'):
                new_zoom = (int(value), int(value))
                self.grid.lat, self.grid.longit, self.grid.lines = set_zoom(self.grid.lines, new_zoom, self.grid.zoom, self.grid.lat, self.grid.longit)
                self.grid.zoom = (float(value), float(value))
                self.zoom_slider.value = float(value)
            elif token[0] == 'colors':
                try:
                    gridR = int(self.config.get('colors', 'r'))
                except:
                    gridR = 0
                try:
                    gridG = int(self.config.get('colors', 'g'))
                except:
                    gridG = 0
                try:
                    gridB = int(self.config.get('colors', 'b'))
                except:
                    gridB = 1
                self.grid.gridColor = (gridR/255.0, gridG/255.0, gridB/255.0)
                # try:
                    # backR = int(self.config.get('colors', 'rb'))
                # except:
                    # backR = 0
                # try:
                    # backG = int(self.config.get('colors', 'gb'))
                # except:
                    # back = 0
                # try:
                    # backB = int(self.config.get('colors', 'bb'))
                # except:
                    # backB = 0
                # self.parent.canvas.add(Color(backR/255.0, backG/255.0, backB/255.0))
            self.grid.refresh_screen()
if __name__ in ('__android', '__main__'):
    PlatformApp().run()
