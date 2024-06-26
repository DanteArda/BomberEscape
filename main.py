import simplegui
from user305_o32FtUyCKk_0 import Vector   

# Player Class #
# =========================================== #
class Player():
    def __init__(self):
        self.Position = None
        self.Lives = 3
        self.Score = 0 
        self.Delayed_Score = 0 # for UI
        self.Bombs_Dropped = 0
        self.Highest_Combo = 0
   
    def f(self, n):
        if n == 0: return 0
        return (300 + (n-1) * 75) + self.f(n-1)
    
    def upScore(self, count):
        self.Score += self.f(count)
    
    def reset(self):
        self.Position = None
        self.Lives = 4
        self.Score = 0 
        self.Delayed_Score = 0 # for UI
        self.Bombs_Dropped = 0
        self.Highest_Combo = 0
        
# =========================================== #

# Actor Class
# =========================================== #
class Actor:
    def __init__(self, position, radius, color):
        self.Position = position
        self.Velocity = Vector()
        self.Radius = radius
        self.Color = color
        self.inCollision = False
        self.ScoreGivenWhenKilled = 300
        
    def draw(self, canvas):
        canvas.draw_circle(self.Position.get_p(), self.Radius, 1, self.Color, self.Color)
        
    def update(self):
        self.Position.add(self.Velocity)
        self.Velocity.multiply(0.85)
        
    def collide(self, other_actor):
        normal = self.position.copy().subtract(other_actor.Position).normalize()
        
        self.Velocity.reflect(normal)
        other_actor.Velocity.reflect(normal)
        
      
class PlayerCharacter(Actor):
    def __init__(self):
        super().__init__(Vector(), 25, "White")
        
        self.delayBetweenBombDrops = 3 # seconds
        self.canDropBomb = False
        
    def update(self):
        self.Position.add(self.Velocity)
        self.Velocity.multiply(0.85)
        

        if (self.timeSinceLastDroppedBomb + 60 * self.delayBetweenBombDrops) <= runtime:
            self.canDropBomb = True
            
    def tookDamage(self):
        Player.Lives -= 1
        Game.reset_stage()
        
class Enemy(Actor):
    def __init__(self, Position, Radius = 25, Velocity = Vector(), AI = False):
        super().__init__(Position, Radius, "Red")
        
        # Supported AI : boolean value
        # "True" : Follows the Player
        # "False" : Default, moves in a straight line, bouncing off walls
        self.AI = AI
        
        
        if Velocity == Vector() or not self.AI:
            self.Velocity = Vector(3.33/2, 3.33/2)
        else:
            self.Velocity = Velocity.copy()
        
    def collide(self, other_actor):
        normal = self.Position.copy().subtract(other_actor.Position).normalize()

        v1_par = self.Velocity.get_proj(normal)
        v1_perp = self.Velocity.copy().subtract(v1_par)

        v2_par = other_actor.Velocity.get_proj(normal)
        v2_perp = other_actor.Velocity.copy().subtract(v2_par)
        
        self.Velocity = v2_par + v1_perp
        other_actor.Velocity = v1_par + v2_perp
        
    def calculateVelocityToReachPlayer(self) -> Vector():
        # to be honest I have no clue why we settled on 3.33/2 for speed
        # probably a lot of trial and error to get the right speed feeling for the enemy
        
        # pursuit
        # it will attempt to 'guess' where the player will goto next using the player's velocity and position
        predictedPlayerCharacterPosition = PlayerCharacter.Position.add(PlayerCharacter.Velocity).copy()
        
        # then use that to calculate its own velocity
        requestedVelocity = (predictedPlayerCharacterPosition.subtract(self.Position)).get_normalized() * 3.33/1.25
        
        return requestedVelocity
        
    def update(self):
        if self.AI:
            self.Velocity = self.calculateVelocityToReachPlayer()
        
        self.Position.add(self.Velocity)
        
        allActorsCopy = Game.Enemies.copy()
        allActorsCopy.append(PlayerCharacter)
        for actor in allActorsCopy:
            if self.hit(actor) and actor != self:
                if actor == PlayerCharacter:
                    PlayerCharacter.tookDamage()
                    
                else:  
                    self.collide(actor)
        
    def hit(self, actor) -> boolean:
        distance = actor.Position.copy().subtract(self.Position).length()
        return distance < (actor.Radius + self.Radius)
# =========================================== #

# Spritesheet Class #
# =========================================== #

class Spritesheet():
    def __init__(self, image_url, columns, rows, numFrames):
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
        
        Game.BombInstance = self
 
       
    def update(self):
        self.Counter += 1
        
        if (self.Born + self.Counter) % 30 == 0:
            self.frameIndex[0] = self.frameIndex[0] + 1
            
            if self.frameIndex[0] == 6:
                self.explode()
            
    def explode(self):
        Game.Entities.append(Explosion(self.Position))
        self.kill()
    
    def kill(self):
        Game.Entities.remove(self)
        Game.BombInstance = None
    
    def draw(self, canvas): 
        canvas.draw_image(self.image,
                          (self.frame_width * self.frameIndex[0] + self.frame_centre_x,
                           self.frame_height * self.frameIndex[1] + self.frame_centre_y),
                          (self.frame_width, self.frame_height),
                          (self.Position.x, self.Position.y),
                          (PlayerCharacter.Radius+20, PlayerCharacter.Radius+25))
        
        
class Explosion(Spritesheet):
    def __init__(self, Position):
        # explosion sprite from:
        # Royal Holloway
        # https://www.cs.rhul.ac.uk/courses/CS1830/sprites/explosion-spritesheet.png
        
        super().__init__("https://www.cs.rhul.ac.uk/courses/CS1830/sprites/explosion-spritesheet.png", 9, 9, 74)
        
        self.Position = Position
        self.Counter = 0
        self.Born = runtime
        self.Radius = PlayerCharacter.Radius+20 * 2.75
        
        self.allActorsHit = []
        
        Game.ExplosionInstance = self
    
    def draw(self, canvas):
        # debug purposes
        # draw's actual collision circle
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
                    self.kill()
                    PlayerCharacter.tookDamage()
                    
                else:
                    if actor in Game.Enemies:
                        if actor not in self.allActorsHit:
                            self.allActorsHit.append(actor)
                            
                        Game.Enemies.remove(actor)
        
        if (self.Born + self.Counter) % 3 == 0:
            self.frameIndex[0] = self.frameIndex[0] % self.columns
            
            if self.frameIndex[0] == 0:
                self.frameIndex[1] = self.frameIndex[1] + 1
            
                if self.frameIndex[1] == self.rows:
                    self.kill()
        
    def kill(self):
        # kill both collision and sprite
        Game.flushToPlayerScore() # flush gathered score to Player class
        Game.ExplosionInstance = None
        Game.Entities.remove(self)

# =========================================== #
    
# Physical Objects #
# =========================================== #
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
# =========================================== #
            
# Interaction
# =========================================== #
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
# =========================================== #        
       
# Worldspace #    
# =========================================== #    
class Worldspace:
    def __init__(self): # cache required objects
        self.NorthWall = Wall('up', Vector(0,-1))
        self.SouthWall = Wall('down', Vector(0,1))
        self.EastWall = Wall('left', Vector(1,0))
        self.WestWall = Wall('right', Vector(-1,0))
         
        self.Border = [self.NorthWall, self.SouthWall, self.EastWall, self.WestWall]
        
        self.Buffer = False
        self.AcknowledgeNewExplosion = False
    
    def Render_Border(self, canvas):
        for border in self.Border:
            border.draw(canvas)
            
    def RenderNextMSG(self, canvas, halt, combo = 1):     
        if halt == combo or halt == 0: return
    
        combo_suffix = ""
        if combo > 1:
            combo_suffix = " x" + str(0.25*(combo - 1) + 1)
        canvas.draw_text("300" + combo_suffix, (70, (Game.SCREEN_HEIGHT / 12) + (45 + 20*(combo-1))), 16, "White")
        
        self.RenderNextMSG(canvas, halt, combo + 1)
        
            
    def RenderScoreQueue(self, canvas):
        killList = Game.returnExplosionCasulties()
        
        
        self.RenderNextMSG(canvas, len(killList) + 1)
        Player.Highest_Combo = max(Player.Highest_Combo, len(killList))
            
        # debug purposes
        # draws the text below the score counter, use to see how the message would display when called
        #canvas.draw_text("300", (70, (Game.SCREEN_HEIGHT / 12) + (45 + 20*0)), 16, "White")
        #canvas.draw_text("300", (70, (Game.SCREEN_HEIGHT / 12) + (45 + 20*2)), 16, "White")
        

        canvas.draw_text("Score: " + str(Player.Delayed_Score), (20, Game.SCREEN_HEIGHT / 7.5), 17, "White")
        
    
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
            canvas.draw_text("The Dark Souls of Puzzle Games", (x,y-50), 17, "Grey","monospace")
            
            canvas.draw_text("Bomber Escape", (x,y), 50, "Red")
            canvas.draw_text("A CS1821 Game", (x,y+25), 20, "Grey")
            
            canvas.draw_text("How to Play:", (x,y+75), 32, "White")
            canvas.draw_text("> Use Arrow Keys to Navigate", (x,y+100),22, "White")
            canvas.draw_text("> Spacebar to drop Bomb", (x,y+125),22, "White")
            canvas.draw_text("> Avoid the Bomb, Kill the Enemies", (x,y+150),22, "White")
            canvas.draw_text("> You ONLY have " + str(Game.TIME_REMAINING) + " seconds", (x,y+175),22, "White")
            canvas.draw_text("> You have Three Lives", (x,y+200),22, "White")
            canvas.draw_text("> Bomb has 3 second fuse time.", (x,y+225),22, "White")
            
            canvas.draw_text("Good Luck!", (x,y+275),28, "White")
            
            if runtime % 60 <= 40: # flashing effect 
                canvas.draw_text("Press [SPACEBAR] to Start Game", (x-60,y+350),32, "Red")
        
        elif stage == -2: # Game Over 
            # Originally this was supposed to show a Game Over screen
            # But in the Games Group Project Requirements, it states:
            # When the lives go to zero, the welcome screen reappears and all the game sprites are cleared.
            pass
            
        elif stage == -3: # win screen
            canvas.draw_text("Congratulations!", (x,y+75), 32, "White")
            canvas.draw_text("SCORE: " + str(Player.Score), (x,y+100),22,"White")
            canvas.draw_text("Highest Combo: " + str(Player.Highest_Combo), (x,y+125),22,"White")
            
            canvas.draw_text("STATS:", (x,y+175),22, "White")
            canvas.draw_text("Bombs Dropped: " + str(Player.Bombs_Dropped), (x,y+200),22, "White")
            canvas.draw_text("Time Took: " + str(Game.TOTAL_TIME - Game.TIME_REMAINING) + " seconds", (x,y+225),22,"White")
            canvas.draw_text("Lives left: " + str(Player.Lives), (x,y+250),22,"White")
        
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
                ## use below to add any extra walls, objects, entities
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
            self.RenderScoreQueue(canvas)
            Game.isPlaying = True
# =========================================== #

# Game Class
# =========================================== #
class Game:
    def __init__(self):
        self.SCREEN_WIDTH = 512
        self.SCREEN_HEIGHT = 512
        
        self.reset()
        
        self.Metatable = {
            1 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : [
                    Enemy(Vector(120,120))
                ]
            },
            2 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : [
                    Enemy(Vector(120,120)), 
                    Enemy(Vector(45,54), 17)
                ]
            },
            3 : {
                "PlayerSpawn" : Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2),
                "EnemySpawn" : [
                    Enemy(Vector(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT/2), 23, Vector(0,3.33/2)),
                    Enemy(Vector(475,250), 25, Vector(), True), 
                ]
            },
        }
        
        
    def flushToPlayerScore(self):
        print("Flushed to Player Score")
        if len(self.returnExplosionCasulties()) > 0:
            Player.upScore(len(self.returnExplosionCasulties()))
        Player.Delayed_Score = Player.Score
        
    def reset(self):
        # __init__
        self.TIME_REMAINING = 100
        self.TOTAL_TIME = self.TIME_REMAINING
        
        self.STAGE = -1
        self.PREVIOUS_STAGE = 1
        self.MAX_LEVEL = 4 # last level + 1
        self.isPlaying = False # Take away player control while render
        
        self.Entities = []
        self.Enemies = []
        self.ObjectPipeline = []
        
        self.ExplosionInstance = None
        self.BombInstance = None
    
    def reset_all(self): # reset the whole game
        # just reset all the init to default
        self.forceKillObj(Bomb)
        self.forceKillObj(Explosion)
        
        self.reset()
        self.ObjectPipeline.clear()
        
        Player.reset()
        
    def reset_stage(self):
        print("Restarting Stage " + str(self.STAGE))
        
        self.forceKillObj(Bomb)
        self.forceKillObj(Explosion)
           
        # Adhoc solution until Metatable being overriden is fixed.
        if self.STAGE == 1:
            PlayerCharacter.Position = Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2)
            self.Enemies = [Enemy(Vector(120,120))]
            
        elif self.STAGE == 2:
            PlayerCharacter.Position = Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2)
            self.Enemies = [Enemy(Vector(120,120)), Enemy(Vector(45,54), 17)]
            
        elif self.STAGE == 3:
            PlayerCharacter.Position = Vector(self.SCREEN_WIDTH / 4,self.SCREEN_HEIGHT / 2)
            self.Enemies = [Enemy(Vector(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT/2), 23, Vector(0,3.33)), Enemy(Vector(475,250), 25, Vector(), True)]
            
        print("OK")
        
    def forceKillObj(self, obj):
        for objInstance in Game.Entities:
            if isinstance(objInstance, obj):
                objInstance.kill()
    
    def Transistion(self): # Whenever moving to new Level        
        PlayerCharacter.Position = self.Metatable[self.STAGE]["PlayerSpawn"]
        print("Moved Player")
        
        self.Enemies = self.Metatable[self.STAGE]["EnemySpawn"]
        print("Spawning Enemies")
        
        print("OK") 
        
    def returnExplosionCasulties(self) -> list:
        if self.ExplosionInstance:
            return self.ExplosionInstance.allActorsHit
        return []
        
    # Game Loop
    # =========================================== #
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
                    Object.update()
                    Object.draw(canvas)
                    
                    PlayerCharacter.update()
                    PlayerCharacter.draw(canvas)
            
            if len(self.Enemies) == 0 and self.isPlaying: # all enemies killed
                if self.PREVIOUS_STAGE + 1 == self.MAX_LEVEL:
                    self.STAGE = -3
                    self.isPlaying = False
                else:
                    PlayerCharacter.canDropBomb = False
                    self.STAGE = 0
                
                
            elif self.TIME_REMAINING <= 0 or Player.Lives <= 0: # ran out of time or lives
                self.reset_all()
                self.STAGE = -1
                self.isPlaying = False
            
            
            if runtime % 60 == 0 and self.STAGE != 0:
                self.TIME_REMAINING -= 1
# =========================================== #
           
    
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
