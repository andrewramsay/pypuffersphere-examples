import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *
import itertools
import pygame,time,sys,random,math
from pypuffersphere.utils import glskeleton, glutils, gloffscreen
from pypuffersphere import sphere_sim
from pypuffersphere import sphere

def spiral_layout(n, C=3.6, phi_range=[0, 2*np.pi/3.0]):
    """Return the spherical co-ordinates [phi, theta] for a uniform spiral layout
    on the sphere, with n points. 
    From Nishio et. al. "Spherical SOM With Arbitrary Number of Neurons and Measure of Suitability" 
    WSOM 2005 pp. 323-330"""    
    phis = []
    thetas = []
    for k in range(n):
        h = (2*k)/float(n-1) - 1
        phi = np.arccos(h)
        if k==0 or k==n-1:
            theta = 0
        else:
            theta = thetas[-1] + (C/np.sqrt(n*(1-h**2)))
            
        phis.append(phi)
        thetas.append(theta)        
    return phis, thetas

if __name__ == "__main__":
    s = sphere_sim.make_viewer()
    size = s.size
    
    def draw_fn():
        global first
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
        glDisable(GL_DEPTH_TEST)
        glClearColor(1,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT)
        sphere_sim.make_grid(size)

        def draw_polar(pts):
            for x,y in pts:
                x,y =  sphere.polar_to_display(x,y,size)
                glVertex2f(x,y)


        rad = 0.03 * np.pi
        phis,thetas = spiral_layout(100)
        for pt in zip(phis,thetas):
            lat, lon = pt
            lat -= np.pi/2
            if lat>-1.4:
                pts = sphere.spherical_circle((lon, lat), rad)
                glColor4f(0.5, 0.5, 0.0, 0.5)
                glBegin(GL_LINE_LOOP)
                draw_polar(pts)
                glEnd()


    s.draw_fn = draw_fn
    s.start()
