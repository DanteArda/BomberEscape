import simplegui
from user305_o32FtUyCKk_0 import Vector

"""
TODO:
Collision
"""

class Player():
    def __init__(self):
        self.Position = None
        self.Lives = 3
        self.Score = 0
        self.Bombs_Dropped = 0

class Actor:
    def __init__(self, position, radius, color):
        self.Position = position
        self.Velocity = Vector()
        self.Radius = radius
        self.Color = color
        
    def draw(self, canvas):
        canvas.draw_circle(self.Position.get_p(), self.Radius, 1, self.Color, self.Color)
        
    def update(self):
        self.Position.add(self.Velocity)
        self.Velocity.multiply(0.85)
        
      
class PlayerCharacter(Actor):
    def __init__(self):
        super().__init__(Vector(), 25, "White")
        
        self.delayBetweenBombDrops = 3 # seconds
        self.canDropBomb = False
        self.timeSinceLastDroppedBomb = -90
        
    def update(self):
        self.Position.add(self.Velocity)
        self.Velocity.multiply(0.85)
        
        if (self.timeSinceLastDroppedBomb + 60 * self.delayBetweenBombDrops) <= runtime:
            self.canDropBomb = True
        
class Enemy(Actor):
    def __init__(self, Position, Radius):
        super().__init__(Position, Radius, "Red")

class Spritesheet():
    def __init__(self, image_url, columns, rows, numFrames):
        # image, center_source, width_height_source, center_dest, width_height_dest, rotation)
        self.image = simplegui.load_image(image_url)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rows = rows
        self.columns = columns
        self.numFrames = numFrames
        self.frameIndex = [0,0]
        
        self.frame_width = self.width / self.columns
        self.frame_height = self.height / self.rows
        self.frame_centre_x = self.frame_width / 2
        self.frame_centre_y = self.frame_height / 2
        
class Explosion(Spritesheet):
    def __init__(self):
        # explosion sprite from:
        # royal holloway
        # https://www.cs.rhul.ac.uk/courses/CS1830/sprites/explosion-spritesheet.png
        
        super().__init__("https://www.cs.rhul.ac.uk/courses/CS1830/sprites/explosion-spritesheet.png", 9, 9, 74)
        # TODO

class Bomb(Spritesheet):
    def __init__(self):
        # bomb sprite from:
        # https://opengameart.org/content/bomb-2     
        super().__init__("https://opengameart.org/sites/default/files/bomb_9.png", 6, 1, 6)
        
        self.Position = PlayerCharacter.Position.copy()
        self.Born = runtime
        self.Counter = 0
        
        PlayerCharacter.canDropBomb = False
        PlayerCharacter.timeSinceLastDroppedBomb = runtime
 
       
    def update(self):
        self.Counter += 1
        
        if (self.Born + self.Counter) % 30 == 0:
            self.frameIndex[0] = self.frameIndex[0] + 1
            
            if self.frameIndex[0] == 6:
                self.explode()
            
    def explode(self):
      
        
        Game.Entities.remove(self)
    
    def draw(self, canvas):
        canvas.draw_image(self.image,
                          (self.frame_width * self.frameIndex[0] + self.frame_centre_x,
                           self.frame_height * self.frameIndex[1] + self.frame_centre_y),
                          (self.frame_width, self.frame_height),
                          (self.Position.x, self.Position.y),
                          (PlayerCharacter.Radius+20, PlayerCharacter.Radius+25))
    
# will definetly need to be revised if any walls are detached from the border
class Wall():
    def __init__(self, orientation, normal):
        # orientation: 'up', 'down', 'left', 'right'
        self.Orientation = orientation
        self.Normal = normal
        self.Border = 30
        self.Radius = (self.Border / 2) - 1
        self.Color = "Grey"
    
    def draw(self, canvas):
        if self.Orientation == 'up':
            canvas.draw_line((0,0), (Game.SCREEN_HEIGHT, 0), self.Border, self.Color)
        
        elif self.Orientation == 'down':
            canvas.draw_line((Game.SCREEN_WIDTH,Game.SCREEN_HEIGHT), (0,Game.SCREEN_WIDTH), self.Border, self.Color)
        
        elif self.Orientation == 'left':
            canvas.draw_line((0,0), (0,Game.SCREEN_WIDTH), self.Border, self.Color)
        
        elif self.Orientation == 'right':
            canvas.draw_line((Game.SCREEN_WIDTH,Game.SCREEN_HEIGHT), (Game.SCREEN_HEIGHT, 0), self.Border, self.Color) 
        
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
        
    def keyboard_handler(self):
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
            
            
        if Keyboard.SPACE and PlayerCharacter.canDropBomb: # bomb
            Game.Entities.append(Bomb())
        
        PlayerCharacter.Velocity.add(Vector(self.horizontal_input_buffer[-1], self.vertical_input_buffer[-1]))
    
    def collision(self):
        Actors = Game.Enemies.copy()
        Actors.append(PlayerCharacter)
        
        for actor in Actors:
            offset_l = actor.Position.x - actor.Radius
            offset_r = actor.Position.x + actor.Radius
            
            offset_u = actor.Position.y - actor.Radius
            offset_d = actor.Position.y + actor.Radius
            
            if (offset_l <= Worldspace.EastWall.Radius):
                actor.Velocity.reflect(Worldspace.EastWall.Normal)
            
            if (offset_r >= Game.SCREEN_WIDTH - Worldspace.WestWall.Radius):
                actor.Velocity.reflect(Worldspace.WestWall.Normal)
           
            if offset_u <= Worldspace.NorthWall.Radius:
                actor.Velocity.reflect(Worldspace.NorthWall.Normal)
                
            if offset_d >= Game.SCREEN_HEIGHT - Worldspace.SouthWall.Radius:
                actor.Velocity.reflect(Worldspace.SouthWall.Normal)
    
    def update(self):
        self.keyboard_handler()
        self.collision()
        
       
class Worldspace:
    def __init__(self): # cache required objects
        self.NorthWall = Wall('up', Vector(0,-1))
        self.SouthWall = Wall('down', Vector(0,1))
        self.EastWall = Wall('left', Vector(1,0))
        self.WestWall = Wall('right', Vector(-1,0))
         
        self.Border = [self.NorthWall, self.SouthWall, self.EastWall, self.WestWall]
    
    def Render_Border(self, canvas):
        for border in self.Border:
            border.draw(canvas)
    
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
            canvas.draw_text("> You ONLY have " + str(Game.TIME_REMAINING) + " seconds", (x,y+175),22, "White")
            canvas.draw_text("> You have Three Lives", (x,y+200),22, "White")
            
            canvas.draw_text("Good Luck!", (x,y+250),28, "White")
            
            if runtime % 60 <= 40: # flashing effect 
                canvas.draw_text("Press Spacebar to Start Game", (x-50,y+300),32, "Red")
        
        elif stage == -2: # Game Over Screen
            pass
            
            
        else:
            if stage == 0: # Exit stage
                # draw without the EAST border
                for border in [self.NorthWall, self.SouthWall, self.WestWall]:
                    border.draw(canvas)
    
                
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
        self.ObjectPipeline = []
        
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
            self.ObjectPipeline = [self.Entities, self.Enemies]
            
            Interaction.update()
            
            print(self.ObjectPipeline)
                                      
            for pipeline in self.ObjectPipeline:
                for Object in pipeline:
                    PlayerCharacter.update()
                    PlayerCharacter.draw(canvas)
                    Object.update()
                    Object.draw(canvas)
            
            
            if len(self.Enemies) == 0: # all enemies killed
                print("Moving to Exit Stage")
                PlayerCharacter.canDropBomb = False
                self.PREVIOUS_STAGE = self.STAGE
                self.STAGE = 0
                
            elif self.TIME_REMAINING <= 0 or Player.Lives == 0: # ran out of time or lives
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
