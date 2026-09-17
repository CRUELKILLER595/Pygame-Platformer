import pygame as p
p.init()
class camera:
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.x=0
        self.y=0
    def world_to_screen(self,world_x,world_y):
        screen_x=world_x-self.x
        screen_y=world_y-self.y
        return (screen_x,screen_y)
    def screen_to_world(self,screen_x,screen_y):
        world_x=screen_x+self.x
        world_y=screen_y+self.y
        return (world_x,world_y)
