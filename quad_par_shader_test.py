import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *
import pygame,time,sys,random,math
from pypuffersphere.utils import gloffscreen, glutils, glskeleton, shader
from pypuffersphere.sphere import sphere_sim
from pypuffersphere.sphere import sphere_cy as sphere
from pypuffersphere.sphere import touch_sphere as touch_lib
import itertools
import pyglet

class RotationManager(object):
    def __init__(self):
        self.rotation = 0
        self.tilt = 0

    def update(self, rotation_delta=0, tilt_delta=0):
        self.rotation += rotation_delta
        self.tilt += tilt_delta 

#  Class for managing a smoothed value
class SmoothedTracker(object):
    def __init__(self, alpha=0.1, max_jump=1e6):
        self.ddelta = 0
        self.last_delta = 0
        self.rotation_angle = 0
        self.last_touched_delta = 0
        self.alpha = alpha
        self.last = None
        self.max_jump = max_jump#
        self.actual_delta = 0

    def reset(self):
        self.last = None

    def update(self, next, touched=True):
        if self.last is None or next is None:
            delta = 0
        else:
            if abs(self.last - next)<self.max_jump:
                delta = -(next - self.last)
            else:
                delta = -(next - self.last)
                delta = self.max_jump * (delta/abs(delta))
        self.last = next

        self.ddelta = self.alpha*(delta - self.last_delta) + (1-self.alpha)*self.ddelta                
        self.last_delta = delta
        ret_val = 0
        if not touched:        
            self.rotation_angle -= self.ddelta
            self.rotation_angle *= 0.7
            if (abs(self.rotation_angle) < 0.1):
                self.rotation_angle = 0            
            #return self.rotation_angle 
            self.last_touched_delta *= 0.91
            ret_val =  self.last_touched_delta
        else:            
            self.last_touched_delta = delta
            self.rotation_angle = 0       

            if abs(delta)<0.5:
                ret_val = 0
            else:
                ret_val = (delta *.8) + (self.last_delta*.2)

        if abs(self.actual_delta)<abs(ret_val) or touched:
            self.actual_delta = 0.8 * self.actual_delta + 0.4*ret_val        
        else:
            self.actual_delta = 0.995 * self.actual_delta + 0.005*ret_val        
        return self.actual_delta



class TouchManager(object):
    def __init__(self):
        if not touch_lib.is_up():
            touch_lib.init(ip="192.168.1.40", fseq=False)
            touch_lib.add_handler()
            touch_lib.start()
        self.drag_touch = None
        self.last_touch = time.clock()

        self.rotation = SmoothedTracker(alpha=0.2, max_jump=20) 
        self.tilt = SmoothedTracker(alpha=0.2, max_jump=20) 

        self.rotation_delta = 0
        self.tilt_delta = 0

        self.touch_points = {}


    def update(self):
        self.touch_points = {}
        rotation_delta, tilt_delta = 0,0

        if touch_lib.is_up():       

            self.touch_points = dict(touch_lib.get_touches())                        
            
            # remove fseq, should it be there
            if -1 in self.touch_points:
                del self.touch_points[-1]

            #  Update Last Touch
            if len(self.touch_points) > 0:
                self.last_touch = time.clock()

            y = None

            #  If our dominant touch is no longer visible
            if not self.touch_points.has_key(self.drag_touch):
                if len(self.touch_points.keys())>0:
                    self.drag_touch = self.touch_points.keys()[0]
                    #self.rotation.reset()
                    #self.tilt.reset()
                    self.rotation.update(None, touched=False)
                    self.tilt.update(None, touched=False)
                    
                else:
                    self.drag_touch = None
                    self.rotation.update(None, touched=False)
                    self.tilt.update(None, touched=False)
                    #self.tilt.reset()

            #  Process current dominant touch
            if self.touch_points.has_key(self.drag_touch):

                x, y = self.touch_points[self.drag_touch]
                yoffset = y
                lat, lon = sphere.tuio_to_polar(x,y)
                
            
                rotation_delta = self.rotation.update(np.degrees(lat))
                tilt_delta = self.tilt.update(np.degrees(lon))
            else:
                if len(self.touch_points)==0:
                    rotation_delta = self.rotation.update(None, touched=False)
                    tilt_delta = self.tilt.update(None, touched=False)
                else:
                    rotaton_delta = self.rotation.update(None)
                    tilt_delta = self.tilt.update(None)

        self.rotation_delta = rotation_delta
        self.tilt_delta = tilt_delta

        return rotation_delta, tilt_delta


if __name__ == "__main__":
    s = sphere_sim.make_viewer()
    size = s.size
    tilt_angle = 0
    rotate_angle = 0
    n = 50000   
    vertices = np.tile(np.random.uniform(-1,1, (n, 3))+ np.array((0,0,-0.5)), (1,4)) .astype(np.float32)
    normals = np.tile(np.random.uniform(-1,1, (n, 3)).astype(np.float32), (1,4))
    colors = np.tile(np.random.uniform(0,1,  (n, 3)).astype(np.float32), (1,4))
    indices = np.arange(len(vertices)).astype(np.uint32)
    velocity = np.array([0,0.001,0], dtype=np.float32)  
    touch = TouchManager()
    
    shaderpath = os.path.join(os.getcwd(), 'shaders')
    
    with open(os.path.join(shaderpath, "shader_sphere_par_quad.vert")) as v:
            v_shader = v.read()
    with open(os.path.join(shaderpath, "shader_sphere.frag")) as f:
            f_shader = f.read()     
        
    print glGetString(GL_SHADING_LANGUAGE_VERSION)
    print glGetString(GL_VERSION)
    shader = shader.Shader(v_shader, f_shader)
        
    def draw_fn():
        global first, vertices, rotate_angle, tilt_angle
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, size, 0, size, -1, 500)
        glMatrixMode(GL_MODELVIEW)    
        glLoadIdentity()
        glEnable(GL_POINT_SMOOTH)
        glPointSize(2.0)
        glColor4f(1,0,1,1)
        glDisable(GL_TEXTURE_2D)
        glLineWidth(2.0)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        rotate, tilt = np.radians(touch.update())
        rotate_angle += rotate
        tilt_angle += tilt

        shader.bind()
        shader.uniformf("resolution", 1920)
        shader.uniformf("rotate", rotate_angle)
        #shader.uniformf("tilt", tilt_angle)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        #glTranslatef(0.1*time.clock(),0,0)
        
        glEnable(GL_PROGRAM_POINT_SIZE)
        pyglet.gl.glVertexPointer(3, GL_FLOAT, 0, vertices.ctypes.data)    
        pyglet.gl.glColorPointer(3, GL_FLOAT, 0, colors.ctypes.data)    
        pyglet.gl.glNormalPointer(GL_FLOAT, 0, normals.ctypes.data)    
        pyglet.gl.glDrawElements(GL_QUADS, len(indices), GL_UNSIGNED_INT, indices.ctypes.data)

        shader.unbind()

    s.draw_fn = draw_fn
    s.start()
