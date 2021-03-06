import kivy
kivy.require('1.0.6')
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle

class Drawable():
    def __init__(self, obj, color = (1, 1, 1, 1), **kwargs):
        self.item = obj(**kwargs)
        self.color = color
        self.point = 'points' in kwargs.keys()

    def change_pos(self, new_pos):
        if self.point:
            change = [self.item.points[0] - new_pos[0], self.item.points[1] - new_pos[1]]
            self.item.points = (new_pos[0],new_pos[1] , self.item.points[2] - change[0], self.item.points[3] - change[1])
        else:
            self.item.pos = new_pos
    
    def translate(self, zoom, ozoom, offx, offy):
        facx = zoom[0] / float(ozoom[0])
        facy = zoom[1] / float(ozoom[1])
        if self.point:
            self.item.points = (self.item.points[0]*facx - offx, self.item.points[1]*facy - offy, self.item.points[2]*facx - offx, self.item.points[3]*facy - offy)
        else:
            self.item.pos = (self.item.pos[0]*facx - offx, self.item.pos[1]*facy - offy)
            self.item.size = (self.item.size[0]*facx, self.item.size[1]*facy)
    
    def draw(self, canvas):
        if self.color != None:
            canvas.add(Color(*self.color))
        else:
            canvas.add(Color())
        canvas.add(self.item)
        
    def collide(self, drawable):
        pos = list(drawable.item.pos)
        
        xLower, xUpper = sorted((self.item.points[0], self.item.points[2]))
        yLower, yUpper = sorted((self.item.points[1], self.item.points[3]))
        
        if (self.point and xLower <= pos[0] <= xUpper
            and (yLower <= pos[1] or yUpper >= pos[1])):
            # Line isnt vertical
            if abs(self.item.points[2] - self.item.points[0]) > 0.1:
                slope = (self.item.points[3] - self.item.points[1]) / (self.item.points[2] - self.item.points[0])
                y2 = slope * (pos[0] + drawable.item.size[0] - self.item.points[0]) + self.item.points[1]
                y1 = slope * (pos[0] - self.item.points[0]) + self.item.points[1]
                
                if (( pos[1] <= y1 <= pos[1] + drawable.item.size[1])
                    or ((pos[1] <= y2 <= pos[1] + drawable.item.size[1]))):
                    return True
            # vertical
            elif yLower <= pos[1] <= yUpper:
                return True
        # polyline - Check distance from center to endpoints
        center = (pos[0] + drawable.item.size[0] / 2.0, pos[1] + drawable.item.size[1] / 2.0)
        distance1 = (xLower - center[0]) ** 2 + (yLower - center[1]) ** 2
        distance2 = (xUpper - center[0]) ** 2 + (yUpper - center[1]) ** 2
        
        if distance1 < drawable.item.size[0] ** 2 or distance2 < drawable.item.size[0] ** 2:
            return True
        
        
        return False
        
    def snap_to(self, lines, zoom, lat, longit): #uses the remainder between the point and the zoom to calculate where the point should snap to
        for line in lines:
            x = (line[0] % zoom[0]) - min(*lat)
            y = (line[1] % zoom[1]) - min(*longit)
            if x >= zoom[0] / 2:
                x = -(zoom[0] - x)
            if y >= zoom[1] / 2:
                y = -(zoom[1] - y)
            line[0] = line[0] - x
            line[1] = line[1] - y
        if lines[0] == lines[1]:
            return False
        self.item.points = (lines[0][0], lines[0][1], lines[1][0], lines[1][1])
        return True
        
    def snap_image(self, pos, zoom, lat, longit): # snaps an image to a cell
        x = (pos[0] % zoom[0]) - min(*lat)
        y = (pos[1] % zoom[1]) - min(*longit)
        if x <= 0:
            x = zoom[0] + x
        if y >= zoom[1]:
            y = y - zoom[1]
        pos[0] = pos[0] - x
        pos[1] = pos[1] - y
        self.item.pos = pos
        
    def snap(self, coord, zoom, lat, longit):
        if self.point:
            return self.snap_to(coord, zoom, lat, longit)
        else:
            return self.snap_image(coord, zoom, lat, longit)
            
    def save(self):
        return {'color': self.color,
                'points': self.item.points,
                'width': self.item.width
               }
    
    def move_points(self, x, y):
        self.item.points = (self.item.points[0] + x, self.item.points[1] + y, self.item.points[2] + x, self.item.points[3] + y)
    def move_pos(self, x, y):
        self.item.pos = (self.item.pos[0] + x, self.item.pos[1] + y)
        
    def move(self, x, y):
        if self.point:
            self.move_points(x, y)
        else:
            self.move_pos(x, y)
            
class Polyline(Widget):
    def __init__(self, color = (1, 1, 1)):
        super(Polyline, self).__init__()
        self.lines = []
        self.color = color
    
    def add_line(self, *points):
        self.lines.append(Drawable(Line, color = self.color, points = points, width = 1))
    
    def erase(self, line):
        self.lines.remove(line)
    
    def collide(self, eraser):
        for line in self.lines:
            if line.collide(eraser):
                self.erase(line)
                return
                
    def save(self):
        return [line.save() for line in self.lines]
        
    def load(self, lines):
        self.color = lines[0]['color']
        for line in lines:
            self.add_line(*line['points'])
                
    def change_pos(self, new_pos):
        for line in self.lines:
            change = [line.points[0] - new_pos[0], line.points[1] - new_pos[1]]
            line.change_pos(change)
            
    def translate(self, zoom, ozoom, offx, offy):
        for line in self.lines:
            line.translate(zoom, ozoom, offx, offy)
    
    def draw(self, canvas):
        for line in self.lines:
            line.draw(canvas)
            
    def snap(self, coord, zoom, lat, longit):
        for line in self.lines:
            line.snap_to(coord, zoom, lat, longit)
            
    def move(self, x, y):
        for line in self.lines:
            line.move_points(x, y)
