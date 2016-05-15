import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *
import pygame,time,sys,random,math,os
from pypuffersphere.utils import gloffscreen, glutils, glskeleton
from pypuffersphere import sphere_sim
from pypuffersphere import sphere_cy as sphere
from pypuffersphere import touch_sphere as touch_lib
import itertools
import pyglet


def safe_exit():
        # touch_lib.stop()        
        sys.exit()



def quad(size):
    """Draw a texture mapped quad of the given size"""
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
    ('v2f', (0,0,size,0,size,size,0,size)),
    ('t2f', (0,0,1,0,1,1,0,1)))
    

class ParallaxLayer(object):
    """Class representing one parallax layer, having a texture,
    a depth (affects rotational speed) and a z_order (order of drawing).
        
    Rotation and tilt of this layer can be set by directly setting the tilt
    and rotation members (e.g. layer.tilt += 1)
    """
    def __init__(self, texture, parallax_speed, z_order, init_rotation=0, init_tilt=0):
        self.texture = texture        
        self.z_order = z_order
        self.rotation = init_rotation
        self.tilt = init_tilt
        self.tilt_speed = parallax_speed
        self.rotate_speed = parallax_speed
        
    def draw(self, size):
        """Draw the layer quad, applying the appropriate rotation and scaling to
        give the parallax spin and tilt."""
        glPushMatrix()        
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glTranslatef(size/2, size/2, 0)
        glRotatef(self.rotation*self.rotate_speed, 0, 0, 1)
        s = self.tilt * self.tilt_speed        
        glScalef(1.0+s,1.0+s, 1)           
        glTranslatef(-size/2, -size/2, 0)        
        quad(size)
        glPopMatrix()
        


class ParallaxSet(object):
    def __init__(self,  filenames, path='.', depth_cue_color=None, speed=1.0, layer_speeds=None):
        """ 
        Create a set of parallax layers from a path and a list of filenames (e.g. "imgs/parallax" and ["layer0.png", "layer1.png"...] etc.)
        Image files should be power-of-2 square images. For the sphere, 2048x2048 is good.
        
        Layers must be in depth order, deepest layer first. If layer_speeds is given, it should specify a parallax rate for each given layer.
        Otherwise the default parallax rate is assigned based on the depth order. 
        
        If not None, depth_cue_color must be a 4-element (r,g,b,a) color for the intermediate depth cueing layers. 
        For example, (0.05, 0.2, 0.2, 0.05) for a dark blue-ish tinting of deeper layers."""
        self.depth_cue_color = depth_cue_color
        images = [pyglet.image.load(os.path.join(path, fname))  for fname in filenames]
        n_images = len(images)
        if layer_speeds is None:
            speeds = [speed*(2.0/((n_images+2)-i))**2 for i in range(n_images)]
        else:
            speeds = [speed*l for l in layer_speeds]
            
        z_orders = [i for i in range(n_images)]
        self.layers = [ParallaxLayer(img.texture, parallax_speed=speed, z_order=z_order) for img, speed, z_order in zip(images, speeds, z_orders)]
        self._tilt = 0
        self._rotation = 0
            
        
    def draw(self, size):
        """Draw the complete layer set, with intermediate depth cue layers if requested."""
        for layer in self.layers:
            glColor4f(1,1,1,1)
            glEnable(GL_TEXTURE_2D)
            layer.draw(size)
            if self.depth_cue_color:                
                glColor4f(*self.depth_cue_color)
                glDisable(GL_TEXTURE_2D)
                quad(size)
                
    @property 
    def tilt(self):
        return self._tilt
        
    @tilt.setter
    def tilt(self, t):
        self._tilt = t
        for layer in self.layers:
            layer.tilt = self._tilt
            
    @property 
    def rotation(self):
        return self._rotation
        
    @rotation.setter
    def rotation(self, t):
        self._rotation = t
        for layer in self.layers:
            layer.rotation = self._rotation
            


class DragHandler(object):
    def __init__(self):
        """Bring up the touch library and start receiving touch events."""
        if not touch_lib.is_up():
            touch_lib.init(ip="192.168.1.40", fseq=False)
            touch_lib.add_handler()
            touch_lib.start()   
        self.touch = None
        self.last_pos = None
        self.delta = None
        
    def update(self):        
       """
       Update the drag state. 
       
       Return the current tracked fingers position, and
       its change since the last call to update, in the form (lon, lat), (d_lon, d_lat).
       Tracks the first finger to go down, and switched to the next finger remaining (if any) if
       that finger is lost. 
       
       Returns None, None if no finger tracked."""
       
       if touch_lib.is_up():       
            touch_points = dict(touch_lib.get_touches())                        
            # remove fseq, should it be there
            del touch_points[-1]
            
            if touch_points.has_key(self.touch):
                x, y = touch_points[self.touch]
                lon, lat = sphere.tuio_to_polar(x,y)
                if self.last_pos is not None:
                    self.delta = (lon-self.last_pos[0], lat-self.last_pos[1])                   
                self.last_pos = (lon, lat)
            else:
                self.last_pos = None
                self.delta = None        
                # assign to next finger on the drag
                if len(touch_points.keys())>0:
                    self.touch = touch_points.keys[0]
                    
            return self.last_pos, self.delta
                
                
if __name__ == "__main__":
    imagepath = os.path.join(os.getcwd(), 'images')
    
    size = 1920   
    s = sphere_sim.make_viewer()
    ls = ['0', '1', '1c', '3', '2', '3c', '4', '5']#, '5b', '6', '7']    
    layer_names = ["layer%s.png"%l for l in ls]    
    layer_set = ParallaxSet(layer_names, path=os.path.join(imagepath, 'DS-parallax'))
    # drag_tracker = DragHandler()    
    
    def redraw():        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        
        glDisable(GL_LIGHTING)      
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, size, 0, size, -1, 500)
        glMatrixMode(GL_MODELVIEW)    
        glLoadIdentity()
        glClearColor(1,1,1,1)
        glDisable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        
        # pos, delta = drag_tracker.update()        
        # tilt = pos[1]
        # rotate_change = delta[0]
        
        # tilt = np.sin(time.clock()) / 10.0
        
        layer_set.draw(size)
        rotate_change = 1
        layer_set.rotation += rotate_change
        # layer_set.tilt = tilt
        
        
        
    
    s.draw_fn = redraw
    s.start()
