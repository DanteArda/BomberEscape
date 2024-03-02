import simplegui
from user305_o32FtUyCKk_0 import Vector

class Player:
    def __init__(self):
        self.lives = 3
        
class Keyboard:
    def __init__(self):
        self.RIGHT = False
        self.LEFT = False
        self.UP = False
        self.DOWN = False
        self.SPACE = False # bomb dropped with space

class Enemy:
    def __init__(self):
        pass

class Interaction: # handles collision checking
    def __init__(self):
        pass

class Game:
    def __init__(self):
        self.SCREEN_HEIGHT = 516
        self.SCREEN_WIDTH = 980
        
        self.current_Level = 0
        self.current_State = "Startup"
        
    def Reset(self): # if player loses all lives
        self.current_Level = 0
        self.current_State = "Startup"
    
    def Draw(self, canvas):
        pass
    
# init class
Game = Game()
    
frame = simplegui.create_frame("Game", Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)
frame.set_draw_handler(Game.Draw)
frame.start()


