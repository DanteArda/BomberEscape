import simplegui
from user305_o32FtUyCKk_0 import Vector

"""
TODO:
There is a realtime score mechanism.

When the lives go to zero, the welcome screen reappears and all the game sprites are cleared.

While the welcome screen is being displayed the game mechanism is stopped.
When the welcome screen is clicked, the lives and the score are reset.
The program displays on the canvas an appropriate text for both the lives and the score.

Pursue and evade effects (e.g., sprites that “gravitate” towards or chase the player).
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
        self.inCollision = False
        
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
        self.hasDroppedBombForFirstTime = False
        
    def update(self):
        self.Position.add(self.Velocity)
        self.Velocity.multiply(0.85)
        

        if (self.timeSinceLastDroppedBomb + 60 * self.delayBetweenBombDrops) <= runtime:
            self.canDropBomb = True
        
class Enemy(Actor):
    def __init__(self, Position, Radius, AI = None):
        super().__init__(Position, Radius, "Red")
        
        # Supported AI
        # "FollowPlayer" : Follows the Player
        # None : Default, moves in a straight line, bouncing off walls
        self.AI = AI
        self.Velocity = Vector(3.33/2, 3.33/2)
        
    def update(self):
        if self.AI == "FollowPlayer":
            pass
        
        self.Position.add(self.Velocity)
        

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
    def __init__(self, Position):
        # explosion sprite from:
        # royal holloway
        # https://www.cs.rhul.ac.uk/courses/CS1830/sprites/explosion-spritesheet.png
        
        super().__init__("https://www.cs.rhul.ac.uk/courses/CS1830/sprites/explosion-spritesheet.png", 9, 9, 74)
        
        self.Position = Position
        self.Counter = 0
        self.Born = runtime
        self.Radius = PlayerCharacter.Radius+20 * 2.75
    
    def draw(self, canvas):
        # debug mode
        # canvas.draw_circle(self.Position.get_p(), self.Radius, 1, "Orange", "Orange")
        
        canvas.draw_image(self.image,
                          (self.frame_width * self.frameIndex[0] + self.frame_centre_x,
                           self.frame_height * self.frameIndex[1] + self.frame_centre_y),
                          (self.frame_width, self.frame_height),
                          (self.Position.x, self.Position.y),
                          (PlayerCharacter.Radius+20 * 9, PlayerCharacter.Radius+20 * 9))
    
    def hit(self, actor) -> boolean:
        distance = actor.Position.copy().subtract(self.Position).length()
        return distance < actor.Radius + self.Radius

    def update(self):
        self.Counter += 1
        
        allActorsCopy = Game.Enemies.copy()
        allActorsCopy.append(PlayerCharacter)
        for actor in allActorsCopy:
            if self.hit(actor):
                if actor == PlayerCharacter:
                    print("Player")
                    
                else:
                    if actor in Game.Enemies:
                        Game.Enemies.remove(actor)
        
        if (self.Born + self.Counter) % 3 == 0:
            self.frameIndex[0] = self.frameIndex[0] % self.columns
            
            if self.frameIndex[0] == 0:
                self.frameIndex[1] = self.frameIndex[1] + 1
            
                if self.frameIndex[1] == self.rows:
                    self.kill()
        
                    
        
    def kill(self):
        # kill both collision and sprite
        Game.Entities.remove(self)

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
        Player.Bombs_Dropped += 1
 
       
    def update(self):
        self.Counter += 1
        
        if (self.Born + self.Counter) % 30 == 0:
            self.frameIndex[0] = self.frameIndex[0] + 1
            
            if self.frameIndex[0] == 6:
                self.explode()
            
    def explode(self):
        Game.Entities.append(Explosion(self.Position))
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
                if not actor.inCollision:
                    actor.Velocity.reflect(Worldspace.EastWall.Normal)
                    actor.inCollision = True
            else:
                actor.inCollision = False        
            
            if (offset_r >= Game.SCREEN_WIDTH - Worldspace.WestWall.Radius) and not (Game.STAGE == 0):
                if not actor.inCollision:
                    actor.Velocity.reflect(Worldspace.WestWall.Normal)
                    actor.inCollision = True
            else:
                actor.inCollision = False
           
            if offset_u <= Worldspace.NorthWall.Radius:
                if not actor.inCollision:
                    actor.Velocity.reflect(Worldspace.NorthWall.Normal)
                    actor.inCollision = True
            else:
                actor.inCollision = False
                
            if offset_d >= Game.SCREEN_HEIGHT - Worldspace.SouthWall.Radius:
                if not actor.inCollision:
                    actor.Velocity.reflect(Worldspace.SouthWall.Normal)
                    actor.inCollision = True
            else:
                actor.inCollision = False
        
    
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
        
        self.Buffer = False
    
    def Render_Border(self, canvas):
        for border in self.Border:
            border.draw(canvas)
    
    def Render(self, canvas, stage):
        # these two values give the headline, you should add to Y to bring text lower
        x = Game.SCREEN_WIDTH / 2 - 150
        y = Game.SCREEN_HEIGHT / 4
        
        if stage == -1: # Welcome Screen
            if Keyboard.SPACE:
                Game.STAGE = 1
                print("Going to Level", Game.STAGE)
                Game.Transistion()
            # Welcome Page
            
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
            canvas.draw_text("Game Over", (x,y+75), 32, "White")
            
        elif stage == -3: # win screen
            canvas.draw_text("Good Job!", (x,y+75), 32, "White")
            canvas.draw_text("STATS:", (x,y+100),22, "White")
            canvas.draw_text("Bombs Dropped: " + str(Player.Bombs_Dropped), (x,y+125),22, "White")
            canvas.draw_text("Time Took: " + str(500 - Game.TIME_REMAINING) + " seconds", (x,y+150),22,"White")
            canvas.draw_text("Lives left: " + str(Player.Lives), (x,y+175),22,"White")
        
        else:
            if stage == 0: # Exit stage
                for border in [self.NorthWall, self.SouthWall, self.EastWall]:
                    border.draw(canvas)
                
                canvas.draw_text("EXIT", (Game.SCREEN_WIDTH / 2 + 150, Game.SCREEN_HEIGHT / 2), 32, "White")
                if runtime % 60 <= 40: # flashing effect 
                    canvas.draw_text(">>>>", (Game.SCREEN_WIDTH / 2 + 150, Game.SCREEN_HEIGHT / 2 + 25), 32, "White")
        
                if PlayerCharacter.Position.x - PlayerCharacter.Radius > Game.SCREEN_WIDTH and not self.Buffer:
                    self.Buffer = True
                    Game.STAGE = min(Game.PREVIOUS_STAGE + 1, Game.MAX_LEVEL)
                    Game.PREVIOUS_STAGE += 1
                    Game.Transistion()
                        
                    self.Buffer = False

            else:
                self.Render_Border(canvas)
                if stage == 1: # Level 1
                    pass

                elif stage == 2:
                    pass

                elif stage == 3:
                    pass

                else: # No more stages, Win Screen
                    Game.STAGE = -3
           
            canvas.draw_text("Stage: " + str(Game.PREVIOUS_STAGE), (Game.SCREEN_WIDTH / 2.5, Game.SCREEN_HEIGHT / 15), 20, "White")
            canvas.draw_text("Time: " + str(Game.TIME_REMAINING), (Game.SCREEN_WIDTH - 110, Game.SCREEN_HEIGHT / 15), 20, "White")
            canvas.draw_text("Lives: " + str(Player.Lives), (20, Game.SCREEN_HEIGHT / 15), 20, "White")
            Game.isPlaying = True
    

class Game:
    def __init__(self):
        self.SCREEN_WIDTH = 512
        self.SCREEN_HEIGHT = 512
        
        self.TIME_REMAINING = 500
        
        self.STAGE = -1
        self.PREVIOUS_STAGE = 1
        self.MAX_LEVEL = 4 # last level + 1
        self.isPlaying = False # Take away player control while render
        
        self.Entities = []
        self.Enemies = []
        self.ObjectPipeline = []
        
        # Enemy init:
        # __init__(self, Position, Radius, AI):
        self.Metatable = {
            1 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : [Enemy(Vector(120,120), 25)]
            },
            2 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : [Enemy(Vector(120,120), 25), Enemy(Vector(45,54), 25)]
            },
            3 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : []
            },
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
            PlayerCharacter.update()
            PlayerCharacter.draw(canvas)
                                      
            for pipeline in self.ObjectPipeline:
                for Object in pipeline:
                    PlayerCharacter.update()
                    PlayerCharacter.draw(canvas)
                    
                    Object.update()
                    Object.draw(canvas)
            
            
            if len(self.Enemies) == 0: # all enemies killed
                if self.PREVIOUS_STAGE + 1 == self.MAX_LEVEL:
                    self.STAGE = -3
                    self.isPlaying = False
                else:
                    PlayerCharacter.canDropBomb = False
                    self.STAGE = 0
                
                
            elif self.TIME_REMAINING <= 0 or Player.Lives == 0: # ran out of time or lives
                self.STAGE = -1
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

# Cache Spritesheets
Bomb()
Explosion(Bomb().Position)

print("Spritesheets Cached")

frame = simplegui.create_frame("Game", Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)
frame.set_draw_handler(Game.Draw)
frame.set_keydown_handler(Keyboard.keyDown)
frame.set_keyup_handler(Keyboard.keyUp)

print("Game Canvas Started")
frame.start()
