import warnings
import os.path
import json
try:
    import matplotlib
except:
    warnings.warn("matplotlib package not installed - debug will not work")
    
try:
    import numpy
except:
    warnings.warn("numpy not found.")
    
try:
    import pygame
except:
    warnings.warn("pygame package not found.")

from globeos.managers.globe import globe
from globeos.managers.scenemanager import scenemanager

def loadscene(scenename, args={}):
    pygame.init()
    gl, screen, params = handleconfig()
    print(params)
    if(params==None):
        sc = scenemanager(gl, screen, scenename, args, calibrate=True)
    else:
        sc = scenemanager(gl, screen, scenename, args)
    sc.start()    
    
def handleconfig():
    params = None
    if(os.path.isfile("config.json")):
        try:
            params = readconfig()
            gl = globe(cfg=params)
            screen = pygame.display.set_mode((params['winsiz'][0], params['winsiz'][1]))
        except:
            gl = globe()
            screen = pygame.display.set_mode((800, 600))
    else:
        gl = globe()
        screen = pygame.display.set_mode((800, 600))
    return gl, screen, params
    
def readconfig():
    cfg = json.load(open("config.json"))
    cfg['srot'] = [0, 0, 0]
    return cfg
    

