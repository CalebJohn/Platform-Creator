import kivy
kivy.require('1.4.1')
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.graphics import Line, Color, Ellipse, Rectangle, Point
from kivy.uix.widget import Widget
from math import fabs
width, height = Window.size
# Window.clearcolor = (1, 1, 1, 1)


def set_zoom(lines, zoom=48): #repopulates lists based on zoom level
    lat = range(0,width, zoom)
    long = range(0, height, zoom)
    for line in lines:
        snap_to(line, zoom)
    return lat, long, lines
    
def snap_to(lines, zoom): #uses the remainder between the point and the zoom to calculate where the point should snap to
    for line in lines:
        x = line[0] % zoom
        y = line[1] % zoom
        if x >= zoom / 2:
            x = -(zoom - x)
        if y >= zoom / 2:
            y = -(zoom - y)
        line[0] = line[0] - x
        line[1] = line[1] - y
    return lines

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
            self.color = (0, 1, 0)
        elif instance.text == 'Brown':
            self.color = (0.5, 0.25, 0.25)
            
    def undo(self, instance):  #removes the last line placed and then redraws the screen
        if self.straight:
            self.lines = self.lines[:-1]
        self.refresh_screen()
        
    def toggle_draw(self, instance): #stops the line from snapping to grid
        self.straight = False
        self.draw = not self.draw
        self.scroll = False
        self.grab = False
    def toggle_straight(self, instance): #gets the line to snap to grid
        self.straight = not self.straight
        self.draw = False
        self.scroll = False
        self.grab = False
    def toggle_scroll(self, instance): #allows user to scroll
        self.straight = False
        self.draw = False
        self.scroll = not self.scroll
        self.grab = False
    def toggle_grab(self, instance): #allows user to grab a line
        self.straight = False
        self.draw = False
        self.scroll = False
        self.grab = not self.grab
        
    def on_startup(self): #defines everything that needs to be defined before startup
        #defines variables to be used
        self.lines = []
        self.draw_lines = []
        self.drawn_lines = []
        self.straight = True
        self.draw = False
        self.scroll = False
        self.grab = False
        self.lat = ()
        self.long = ()
        self.zoom = height/12
        self.x = self.y = 0
        self.color = (1, 1, 1)
        
        #creates all buttons used
        self.btnw = Button(text = 'White', pos = (0, self.zoom), size = (self.zoom, self.zoom), background_color = (1, 1, 1, 0.9))
        self.btnr = Button(text = 'Red', pos = (self.zoom, self.zoom), size = (self.zoom, self.zoom), background_color = (1, 0, 0, 0.9))
        self.btnb = Button(text = 'Blue', pos = (self.zoom*2, self.zoom), size = (self.zoom, self.zoom), background_color = (0, 0, 1, 0.9))
        self.btny = Button(text = 'Yellow', pos = (self.zoom*3, self.zoom), size = (self.zoom, self.zoom), background_color = (1, 1, 0, 0.9))
        self.btng = Button(text = 'Green', pos = (self.zoom*4, self.zoom), size = (self.zoom, self.zoom), background_color = (0, 1, 0, 0.9))
        self.btnbr = Button(text = 'Brown', pos = (self.zoom*5, self.zoom), size = (self.zoom, self.zoom), background_color = (1, 0.5, 0.5, 1))
        self.btnline = ToggleButton(state = 'down', group = 'state', background_normal = 'images/line.png', background_down = 'images/lined.png', pos = (self.zoom, 0), size = (self.zoom, self.zoom))
        self.btnm = ToggleButton(group = 'state', background_normal = 'images/4_point.png', background_down = 'images/4_pointd.png', pos = (self.zoom*2, 0), size = (self.zoom, self.zoom))
        self.btnc = ToggleButton(group = 'state', background_normal = 'images/cursor.png', background_down = 'images/cursord.png', pos = (self.zoom*3, 0), size = (self.zoom, self.zoom))
        self.btndraw = ToggleButton(group = 'state', text = 'Draw', pos = (self.zoom*4, 0), size = (self.zoom, self.zoom))
        self.btnback = Button(background_normal = 'images/back.png', background_down = 'images/backd.png', pos = (self.zoom*5, 0), size = (self.zoom, self.zoom))
        
        #binds buttons to various functions
        self.btnw.bind(on_release = self.color_change)
        self.btnr.bind(on_release = self.color_change)
        self.btnb.bind(on_release = self.color_change)
        self.btny.bind(on_release = self.color_change)
        self.btng.bind(on_release = self.color_change)
        self.btnbr.bind(on_release = self.color_change)
        self.btnback.bind(on_release = self.undo)
        self.btndraw.bind(on_release = self.toggle_draw)
        self.btnline.bind(on_release = self.toggle_straight)
        self.btnm.bind(on_release = self.toggle_scroll)
        self.btnc.bind(on_release = self.toggle_grab)
        
        #calculates the grid used then refreshes screen
        # self.lat, self.long, self.lines = set_zoom(self.lines, self.zoom)
        # self.refresh_screen()
    def refresh_screen(self):
        self.canvas.clear()
            
        #draws lines that the user has drawn
        for line in self.lines:
            self.canvas.add(Color(*line[1]))
            self.canvas.add(line[0])
            
    def on_touch_down(self, touch): #defines the starting point of a new line
        if touch.y < self.zoom*2 and touch.x < self.zoom*6:
            pass
        elif self.straight:
            self.coord = [[touch.x, touch.y]]
        else: self.coord = 0
        
    def on_touch_up(self, touch):
        if touch.y < self.zoom*2 and touch.x < self.zoom*6:
            pass
        elif self.straight and self.coord:
            self.coord.append([touch.x, touch.y]) #defines end point of new line
            self.coord = snap_to(self.coord, self.zoom) #moves points onto grid
            line = [Line(points = (self.coord[0][0], self.coord[0][1], self.coord[1][0], self.coord[1][1]), width = 2), self.color]
            self.lines.append(line)
            self.coord = []
            self.refresh_screen()
        self.x = self.y = 0 # resets variables for finger lines
    def on_touch_move(self, touch):
        if touch.y < self.zoom*2 and touch.x < self.zoom*6:
            pass
        elif self.straight or self.draw:
            if not self.x or not self.y:
                self.x, self.y = touch.x, touch.y #sets the start point of line
            if not self.coord:
                self.coord = [[touch.x, touch.y]] #used as a start point if finger just entered screen
            self.canvas.add(Color(*self.color))
            line = Line(points = (self.x, self.y, touch.x, touch.y), width = 1)  #draws a line that follows the users finger
            self.canvas.add(line)
            self.x, self.y = touch.x, touch.y #updates points
            
                
        elif self.scroll:
            pass
            
            

class PlatformApp(App):
    def color_toggle(self, instance): # def function that raises buttons
        if instance.state == 'down':
            self.parent.add_widget(self.main.btnw)
            self.parent.add_widget(self.main.btnr)
            self.parent.add_widget(self.main.btnb)
            self.parent.add_widget(self.main.btny)
            self.parent.add_widget(self.main.btng)
            self.parent.add_widget(self.main.btnbr)
        else:
            self.parent.remove_widget(self.main.btnw)
            self.parent.remove_widget(self.main.btnr)
            self.parent.remove_widget(self.main.btnb)
            self.parent.remove_widget(self.main.btny)
            self.parent.remove_widget(self.main.btng)
            self.parent.remove_widget(self.main.btnbr)
            
    def build(self):
        self.parent = Widget()
        self.main = Platform_draw()
        self.main.on_startup()
        self.main.lat, self.main.long, self.main.lines = set_zoom([], self.main.zoom)
        
        #draws grid lines
        for x in self.main.lat:
            self.parent.canvas.add(Color(0, 0, 1))
            self.parent.canvas.add(Line(points = (x, 0, x, height), width = 1))
        for y in self.main.long:
            self.parent.canvas.add(Color(0, 0, 1))
            self.parent.canvas.add(Line(points = (0, y, width, y), width = 1))
        btncolor = ToggleButton(group = 'a', text = 'Color', pos = (0, 0), size = (self.main.zoom, self.main.zoom))
        
        # adds buttons to screen
        # self.parent.add_widget(btncolor)
        self.parent.add_widget(self.main.btnm)
        self.parent.add_widget(self.main.btnc)
        self.parent.add_widget(self.main.btndraw)
        self.parent.add_widget(self.main.btnback)
        self.parent.add_widget(self.main.btnline)
        
        
        #adds the self.main class
        # btncolor.bind(on_release = self.color_toggle)
        self.parent.add_widget(self.main)
        
        #adds color buttons
        self.parent.add_widget(self.main.btnw)
        self.parent.add_widget(self.main.btnr)
        self.parent.add_widget(self.main.btnb)
        self.parent.add_widget(self.main.btny)
        self.parent.add_widget(self.main.btng)
        self.parent.add_widget(self.main.btnbr)
       
        return self.parent
        
if __name__ in ('__android', '__main__'):
    PlatformApp().run()
