import simplegui
from user305_o32FtUyCKk_0 import Vector

class Player():
    def __init__(self):
        self.Position = None
        self.Lives = 3
        self.Score = 0
        self.Bombs_Dropped = 0

class Actor:
    def __init__(self):
        self.Position = Vector()
        self.Velocity = Vector()
        self.Radius = 50
        
    def draw(self, canvas):
        canvas.draw_circle(self.Position.get_p(), self.Radius, 1, self.Color, self.Color)
        
        
class PlayerCharacter(Actor):
    def __init__(self):
        self.Position = Vector()
        self.Velocity = Vector()
        self.Radius = 25
        self.Color = "White"
    
    def update(self):
        self.Position.add(self.Velocity)
        self.Velocity.multiply(0.85)
        
    def place_bomb(self):
        pass
        
class Enemy(Actor):
    def __init__(self, Position, Radius):
        self.Position = Position
        self.Velocity = Vector()
        self.Radius = Radius
        self.Color = "Red"
        
    def update(self):
        self.Position.add(self.Velocity)

class Bomb:
    def __init__(self):
        self.FUSE_TIME = 3

class Keyboard:
    def __init__(self):
        self.RIGHT = False
        self.LEFT = False
        self.UP = False
        self.DOWN = False
        self.SPACE = False # bomb dropped with space
        
    def keyDown(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.RIGHT = True
        if key == simplegui.KEY_MAP['left']:
            self.LEFT = True
        if key == simplegui.KEY_MAP['up']:
            self.UP = True
        if key == simplegui.KEY_MAP['down']:
            self.DOWN = True
        if key == simplegui.KEY_MAP['space']:
            self.SPACE = True

    def keyUp(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.RIGHT = False
        if key == simplegui.KEY_MAP['left']:
            self.LEFT = False
        if key == simplegui.KEY_MAP['up']:
            self.UP = False
        if key == simplegui.KEY_MAP['down']:
            self.DOWN = False
        if key == simplegui.KEY_MAP['space']:
            self.SPACE = False

class Interaction: # handles collision checking   
    def __init__(self):
        self.horizontal_input_buffer = [0]
        self.vertical_input_buffer = [0]
    
    def update(self):
        SPEED= 0.5
        
        # keyboard events
        if Keyboard.RIGHT and SPEED not in self.horizontal_input_buffer:
            self.horizontal_input_buffer.append(SPEED)
            
        if Keyboard.LEFT and -SPEED not in self.horizontal_input_buffer:
            self.horizontal_input_buffer.append(-SPEED)
            
        if Keyboard.UP and -SPEED not in self.vertical_input_buffer:
            self.vertical_input_buffer.append(-SPEED)
        
        if Keyboard.DOWN and SPEED not in self.vertical_input_buffer:
            self.vertical_input_buffer.append(SPEED)
            
        
        if not Keyboard.RIGHT and SPEED in self.horizontal_input_buffer:
            self.horizontal_input_buffer.remove(SPEED)
            
        if not Keyboard.LEFT and -SPEED in self.horizontal_input_buffer:
            self.horizontal_input_buffer.remove(-SPEED)
            
        if not Keyboard.UP and -SPEED in self.vertical_input_buffer:
            self.vertical_input_buffer.remove(-SPEED)
        
        if not Keyboard.DOWN and SPEED in self.vertical_input_buffer:
            self.vertical_input_buffer.remove(SPEED)
        
        PlayerCharacter.Velocity.add(Vector(self.horizontal_input_buffer[-1], self.vertical_input_buffer[-1]))
            
        
       
class Worldspace:
    def Render_Border(self, canvas):
        canvas.draw_line((0,0), (Game.SCREEN_HEIGHT, 0), 30, "Grey")
        canvas.draw_line((0,0), (0,Game.SCREEN_WIDTH), 30, "Grey")
        canvas.draw_line((Game.SCREEN_WIDTH,Game.SCREEN_HEIGHT), (0,Game.SCREEN_WIDTH), 30, "Grey")
        canvas.draw_line((Game.SCREEN_WIDTH,Game.SCREEN_HEIGHT), (Game.SCREEN_HEIGHT, 0), 30, "Grey")
    
    def Render(self, canvas, stage):
        if stage == -1: # Welcome Screen
            if Keyboard.SPACE:
                Game.STAGE = 1
                print("Going to Level", Game.STAGE)
                Game.Transistion()
            # Welcome Page
            
            # these two values give the headline, you should add to Y to bring text lower
            x = Game.SCREEN_WIDTH / 2 - 150
            y = Game.SCREEN_HEIGHT / 4
            
            canvas.draw_text("Bomber Escape", (x,y), 50, "Red")
            canvas.draw_text("A CS1821 Game", (x,y+25), 20, "Grey")
            
            canvas.draw_text("How to Play:", (x,y+75), 32, "White")
            canvas.draw_text("> Use Arrow Keys to Navigate", (x,y+100),22, "White")
            canvas.draw_text("> Spacebar to drop Bomb", (x,y+125),22, "White")
            canvas.draw_text("> Avoid the Bomb, Kill the enemies", (x,y+150),22, "White")
            canvas.draw_text("> You have a Time Limit", (x,y+175),22, "White")
            canvas.draw_text("> You have Three Lives", (x,y+200),22, "White")
            
            canvas.draw_text("Good Luck!", (x,y+250),28, "White")
            
            if runtime % 60 <= 40: # flashing effect 
                canvas.draw_text("Press Spacebar to Start Game", (x-50,y+300),32, "Red")
        
        elif stage == -2: # Game Over Screen
            pass
            
            
        else:
            if stage == 0: # Exit stage
                # draw without the EAST border
                canvas.draw_line((0,0), (Game.SCREEN_HEIGHT, 0), 30, "Grey")
                canvas.draw_line((0,0), (0,Game.SCREEN_WIDTH), 30, "Grey")
                canvas.draw_line((Game.SCREEN_WIDTH,Game.SCREEN_HEIGHT), (0,Game.SCREEN_WIDTH), 30, "Grey")
                
                canvas.draw_text("EXIT", (Game.SCREEN_WIDTH / 2 + 150, Game.SCREEN_HEIGHT / 2), 32, "White")
                if runtime % 60 <= 40: # flashing effect 
                    canvas.draw_text(">>>>", (Game.SCREEN_WIDTH / 2 + 150, Game.SCREEN_HEIGHT / 2 + 25), 32, "White")
        
            elif stage == 1: # Level 1
                self.Render_Border(canvas)
                
                
            else: # No more stages, Win Screen
                pass
            
            canvas.draw_text("Time: " + str(Game.TIME_REMAINING), (Game.SCREEN_WIDTH - 110, Game.SCREEN_HEIGHT / 15), 20, "White")
            canvas.draw_text("Lives: " + str(Player.Lives), (20, Game.SCREEN_HEIGHT / 15), 20, "White")
            Game.isPlaying = True
    

class Game:
    def __init__(self):
        self.SCREEN_WIDTH = 512
        self.SCREEN_HEIGHT = 512
        
        self.TIME_REMAINING = 500
        
        self.STAGE = -1
        self.PREVIOUS_STAGE = None
        self.isPlaying = False # Take away player control while render
        
        self.Entities = []
        self.Enemies = []
        
        self.Metatable = {
            1 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : [Enemy(Vector(200,200), 20)]
            }
        }
    
    def Transistion(self): # Whenever moving to new Level
        PlayerCharacter.Position = self.Metatable[self.STAGE]["PlayerSpawn"]
        print("Moved Player")
        
        for Enemy in self.Metatable[self.STAGE]["EnemySpawn"]:
            self.Enemies.append(Enemy)
        print("Spawning Enemies")
        
        print("Ready!")
        
    def Draw(self, canvas):
        global runtime
        runtime += 1
        
        Worldspace.Render(canvas, self.STAGE)
        
        if self.isPlaying:
            
            Interaction.update()
            
            PlayerCharacter.update()
            PlayerCharacter.draw(canvas)
                                      
            for Enemy in self.Enemies:
                Enemy.update()
                Enemy.draw(canvas)
            
            
            if len(self.Enemies) == 0: # all enemies killed
                self.PREVIOUS_STAGE = self.STAGE
                self.STAGE = 0
                
            elif self.TIME_REMAINING <= 0 or Player.Lives == 0: 
                # ran out of time or lives
                self.PREVIOUS_STAGE = self.STAGE
                self.STAGE = -2
                self.isPlaying = False
            
            
            if runtime % 60 == 0 and self.STAGE != 0:
                self.TIME_REMAINING -= 1
    
# init class
runtime = 0
Game = Game()
Player = Player()
PlayerCharacter = PlayerCharacter()
Interaction = Interaction()
Worldspace = Worldspace()
Keyboard = Keyboard()

print("Classes Initalised")

frame = simplegui.create_frame("Game", Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)
frame.set_draw_handler(Game.Draw)
frame.set_keydown_handler(Keyboard.keyDown)
frame.set_keyup_handler(Keyboard.keyUp)

print("Game Canvas Started")
frame.start()



