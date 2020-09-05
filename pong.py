import pygame, sys, ast
from pygame.locals import *

#Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

low_bar_size = 100

#Arbitrary window dimensions
window_width = 1000
window_height = 700

#Line thickness set to 20
line_thickness = 20

#Create the main window with the given dimensions
display_surf = pygame.display.set_mode((window_width, window_height+low_bar_size))

#Set frames per second on the game clock
fps_clock = pygame.time.Clock()
fps = 200 # Number of frames per second

game = None

#Whether or not the ball path lines are visible
visible = False

#Whether or not the user is currently controlling a paddle
user_controlled = True

#Whether the game stats are being displayed or not
show_stats = False

class Game():
    #Class is used to create and update the arena along with its contents
    
    def __init__(self, line_thickness=20, speed=1, iteration=0):
        self.line_thickness = line_thickness
        self.speed = speed
        self.hits = 0
        self.wins = 0
        self.losses = 0
        self.iteration = iteration
        
        #Initiate variable and set starting positions
        #any future changes made within rectangles
        ball_x = int(window_width/2 - self.line_thickness/2)
        ball_y = int(window_height/2 - self.line_thickness/2)
        self.ball = Ball(ball_x,ball_y,self.line_thickness,
                         self.line_thickness,self.speed)
        self.paddles = {}
        paddle_height = 100
        paddle_width = self.line_thickness
        user_paddle_x = window_width - paddle_width - 40
        computer_paddle_x = 40
        self.paddles['user'] = Paddle(user_paddle_x,
                                      paddle_width, paddle_height)
        self.paddles['computer'] = AutoPaddle(computer_paddle_x,
                                              paddle_width, paddle_height,
                                              self.ball, self.speed)
        self.scoreboard = Scoreboard(0, 0, 0, iteration=self.iteration)
        
        self.settings = Settings(self)
        

    #Draws the arena the game will be played in. 
    def draw_arena(self):
        display_surf.fill((0,0,0))
        #Draw outline of arena
        pygame.draw.rect(display_surf, WHITE,
                         ((0,0),(window_width,window_height)),
                         self.line_thickness*2)
        #Draw centre line
        pygame.draw.line(display_surf, WHITE,
                         (int(window_width/2),0),
                         (int(window_width/2),window_height),
                         int(self.line_thickness/4))
        
        self.settings.drawBar()

    def update(self):
        self.ball.move()
        self.paddles['computer'].move()

        if self.ball.hit_paddle(self.paddles['computer']):
            self.ball.bounce('x')
        elif self.ball.hit_paddle(self.paddles['user']):
            self.ball.bounce('x')
            self.hits += 1
        elif self.ball.pass_computer():
            self.losses += 1
        elif self.ball.pass_player():
            self.wins += 1

        self.draw_arena()
        self.ball.draw()
        self.paddles['user'].draw()
        self.paddles['computer'].draw()
        self.scoreboard.display(self.hits, self.wins, self.losses)
        self.settings.updateLabels()

class Paddle(pygame.sprite.Sprite):
    def __init__(self,x,w,h):
        self.x = x
        self.w = w
        self.h = h
        self.y = int(window_height / 2 - self.h / 2)
        #Creates Rectangle for paddle.
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    #Draws the paddle
    def draw(self):
        #Stops paddle moving too low
        if self.rect.bottom > window_height - self.w:
            self.rect.bottom = window_height - self.w
        #Stops paddle moving too high
        elif self.rect.top < self.w:
            self.rect.top = self.w
        #Draws paddle
        pygame.draw.rect(display_surf, WHITE, self.rect)

    #Moves the paddle
    def move(self,value):
        self.rect.y += value

class AutoPaddle(Paddle):
    def __init__(self,x,w,h,ball,speed):
        super().__init__(x,w,h)
        self.ball = ball
        self.speed = speed
     
    def move(self):
        #if ball moving towards bat, track its movement. 
        if self.ball.dir_x == -1:
            if self.rect.centery < self.ball.rect.centery:
                self.rect.y += self.speed
            else:
                self.rect.y -= self.speed

class Ball(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h,speed):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = speed
        self.dir_x = -1  ## -1 = left 1 = right
        self.dir_y = -1 ## -1 = up 1 = down
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.path = Path(self.rect.centerx, self.rect.centery, self.dir_x, self.dir_y)

    #draws the ball
    def draw(self):
        self.path.update(self.rect.centerx, self.rect.centery, self.dir_x, self.dir_y)
        pygame.draw.rect(display_surf, WHITE, self.rect)
        

    #moves the ball returns new position
    def move(self):
        self.rect.x += (self.dir_x * self.speed)
        self.rect.y += (self.dir_y * self.speed)

        #Checks for a collision with a wall, and 'bounces' ball off it.
        if self.hit_ceiling() or self.hit_floor():
            self.bounce('y')
        if self.hit_wall():
            self.bounce('x')

    def bounce(self,axis):
        if axis == 'x':
            self.dir_x *= -1
        elif axis == 'y':
            self.dir_y *= -1

    def hit_paddle(self,paddle):
        
        if pygame.sprite.collide_rect(self,paddle):
            return True
        else:
            return False

    def hit_wall(self):
        if ((self.dir_x == -1 and self.rect.left <= self.w) or
            (self.dir_x == 1 and self.rect.right >= window_width - self.w)):
            return True
        else:
            return False

    def hit_ceiling(self):
        if self.dir_y == -1 and self.rect.top <= self.w:
            return True
        else:
            return False

    def hit_floor(self):
        if self.dir_y == 1 and self.rect.bottom >= window_height - self.w:
            return True
        else:
            return False

    def pass_player(self):
        if self.rect.left <= self.w:
            self.rect.x = int(window_width/2)
            self.rect.y = int(window_height/2)
            return True
        else:
            return False

    def pass_computer(self):
        if self.rect.right >= window_width - self.w:
            self.rect.x = int(window_width/2)
            self.rect.y = int(window_height/2)
            return True
        else:
            return False
        
class Path(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.end_x, self.end_y = self.getEnd()
        
        
    def getEnd(self):
        endX = self.x
        endY = self.y
        self.path = None
        while endX != line_thickness+2 and endY != line_thickness*1.5 and endX != window_width-line_thickness-2 and endY != window_height-(line_thickness*1.5):
            endX += self.dir_x
            endY += self.dir_y
        
        if endY == line_thickness*1.5:
            bounce = Path(endX, endY+1, self.dir_x, self.dir_y*-1)
            self.path = bounce
        elif endY == window_height-(line_thickness*1.5):
            bounce = Path(endX, endY-1, self.dir_x, self.dir_y*-1)
            self.path = bounce
        return endX, endY
    
    def getAbsoluteEnd(self):
        absEndX = self.end_x
        absEndY = self.end_y
        found = False
        while found == False:
            if(self.path == None):
                if self.dir_y == -1:
                    absEndY = self.end_y + 40
                else:
                    absEndY = self.end_y - 40
                return True, self.end_x, absEndY
            else:
                found, absEndX, absEndY = self.path.getAbsoluteEnd()
        
        
        return found, absEndX, absEndY
                
    def update(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.end_x, self.end_y = self.getEnd()
        self.draw()
        
    def draw(self):
        global visible
        if visible:
            pygame.draw.line(display_surf, (255, 0, 0), (self.x, self.y), (self.end_x, self.end_y), 5)
            if self.path != None:
                self.path.draw()
            #throwaway, absEndX, absEndY = self.getAbsoluteEnd()
            #pygame.draw.circle(display_surf, (0, 255, 0), (absEndX, absEndY), 5)
                

class Scoreboard():
    def __init__(self,score=0,wins=0,losses=0,x=(window_width/2)+10,y=25,font_size=20, iteration=0):
        self.hits = score
        self.wins = wins
        self.losses = losses
        self.x = x
        self.y = y
        self.iteration = iteration
        self.font = pygame.font.Font('freesansbold.ttf', font_size)

    #Displays the current score on the screen
    def display(self, hits, wins, losses):
        self.hits = hits
        self.wins = wins
        self.losses = losses
        if show_stats:
            result_surf = self.font.render('Iteration: ' + str(self.iteration), True, WHITE)
            rect = result_surf.get_rect()
            rect.topleft = (self.x, self.y)
            display_surf.blit(result_surf, rect)
            
            result_surf = self.font.render('Hits: ' + str(self.hits), True, WHITE)
            rect = result_surf.get_rect()
            rect.topleft = (self.x, self.y+20)
            display_surf.blit(result_surf, rect)
            
            result_surf = self.font.render('Times Scored: ' + str(self.wins), True, WHITE)
            rect = result_surf.get_rect()
            rect.topleft = (self.x, self.y+40)
            display_surf.blit(result_surf, rect)
            
            result_surf = self.font.render('Times Scored on: ' + str(self.losses), True, WHITE)
            rect = result_surf.get_rect()
            rect.topleft = (self.x, self.y+60)
            display_surf.blit(result_surf, rect)
            
            if (self.hits > 0 and self.losses > 0):
                hitsperloss = float(self.hits)/float(self.losses)
            elif self.hits > 0:
                hitsperloss = self.hits
            else:
                hitsperloss = 0
                
            result_surf = self.font.render('Hits per Lost Point: %.2f' %(hitsperloss), True, WHITE)
            rect = result_surf.get_rect()
            rect.topleft = (self.x, self.y+80)
            display_surf.blit(result_surf, rect)
            
class Settings():
    def __init__(self, game):
        global low_bar_size
        self.game = game
        self.bar_size = low_bar_size
        self.font = pygame.font.SysFont("nirmalaui", 15)
        self.buttons = {}
        self.labels = []
        self.label_rects = []
        self.initializeButtons()
        self.loadSettings()
    
    def updateLabels(self):
        self.labels[0] = self.font.render("Speed: " + str(self.game.speed), True, BLACK)
        self.labels[1] = self.font.render("FPS: " + str(fps), True, BLACK)
        self.drawLabels()
        
    def addButton(self, button):
        self.buttons[button.name] = button
        
    def drawBar(self):
        pygame.draw.rect(display_surf, WHITE, ((0, window_height), ((window_width, window_height+self.bar_size))))
        self.drawButtons()
        self.drawLabels()
        
    def drawButtons(self):
        for button in self.buttons.values():
            button.draw()
            
    def drawLabels(self):
        for i in range(len(self.labels)):
            pygame.draw.rect(display_surf, WHITE, self.label_rects[i])
            display_surf.blit(self.labels[i], self.label_rects[i])
        
    def initializeButtons(self):
        speed_down = Button('speed_down', line_thickness, window_height, 30, 30, GRAY, "-")
        self.addButton(speed_down)
        
        
        speed_label = self.font.render("Speed: " + str(self.game.speed), True, BLACK)
        speed_rect = pygame.Rect(speed_down.x + speed_down.w + line_thickness, speed_down.y, 90, 30)
        
        self.labels.append(speed_label)
        self.label_rects.append(speed_rect)
        
        speed_up = Button('speed_up', speed_down.x + speed_down.w + line_thickness*2 + 70, speed_down.y, speed_down.w, speed_down.h, GRAY, "+")
        self.addButton(speed_up)
        
        fps_down = Button('fps_down', speed_up.x + speed_up.w + line_thickness, speed_up.y, speed_up.w, speed_up.h, GRAY, "-")
        self.addButton(fps_down)
        
        fps_label = self.font.render("FPS: " + str(fps), True, BLACK)
        fps_rect = pygame.Rect(fps_down.x + fps_down.w + line_thickness, fps_down.y, 90, 30)
        
        self.labels.append(fps_label)
        self.label_rects.append(fps_rect)
        
        fps_up = Button('fps_up', fps_down.x + fps_down.w + line_thickness*2 + 70, speed_up.y, speed_up.w, speed_up.h, GRAY, "+")
        self.addButton(fps_up)
        
        control = Button('control', line_thickness, speed_down.y + speed_down.h + line_thickness, 160, speed_down.h, GRAY, "Toggle Control")
        self.addButton(control)
        
        lines = Button('lines', line_thickness + control.x + control.w, control.y, control.w, control.h, GRAY, "Toggle Ball Path")
        self.addButton(lines)
        
        stats = Button('stats', lines.x + lines.w + line_thickness, lines.y, lines.w, lines.h, GRAY, "Toggle Stats")
        self.addButton(stats)
        
    def loadSettings(self):
        f = open("settings.txt", "r")
        self.settings = ast.literal_eval(f.readline())
        f.close()
        
        self.updateFPS(self.settings['fps'])
        self.toggleLines(self.settings['lines'])
        self.updateSpeed(self.settings['speed'])
        self.toggleControl(self.settings['user_controlled'])
        self.toggleStats(self.settings['show_stats'])
    
    def saveSettings(self):
        f = open("settings.txt", "w")
        f.write(str(self.settings))
        f.close()
    
    def updateFPS(self, new):
        if new > 0 and new <= 1500:
            global fps
            fps = new
            self.settings['fps'] = new
        
    def toggleLines(self, new):
        global visible
        visible = new
        self.settings['lines'] = new
    
    def updateSpeed(self, new):
        if new >= 0 and new <= 15:
            self.game.speed = new
            self.game.ball.speed = new
            self.game.paddles['user'].speed = new
            self.game.paddles['computer'].speed = new
            self.settings['speed'] = new
        
    def toggleControl(self, new):
        global user_controlled
        user_controlled = new
        self.settings['user_controlled'] = new
        
    def toggleStats(self, new):
        global show_stats
        show_stats = new
        self.settings['show_stats'] = new
        
class Button():
    def __init__(self, name, x, y, w, h, color, text):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.font_color = BLACK
        self.rect = pygame.Rect(x, y, w, h)
        self.font = pygame.font.SysFont('nirmalaui', 20)
        self.text = self.font.render(text,True,self.font_color)
        self.text_rect = self.text.get_rect(center=self.rect.center)
        
    def draw(self):
        pygame.draw.rect(display_surf, self.color, self.rect)
        display_surf.blit(self.text, self.text_rect)
        
    def isClicked(self, event):
        if self.rect.collidepoint(event.pos):
            return True
        else:
            return False

class RunGame():
    #Main function
    def run():
        pygame.init()
        pygame.display.set_caption('Pong')
        pygame.mouse.set_visible(0) # make cursor invisible
        
        global game
        game = Game(speed=5, iteration=0)
        
        while True: #main game loop
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                game.paddles['user'].move(-1*game.speed)
            elif keys[pygame.K_DOWN]:
                game.paddles['user'].move(game.speed)
    
            game.update()
            pygame.display.update()
            fps_clock.tick(fps)
            
    def controlled_run(self, wrapper, iteration):
        pygame.init()
        pygame.display.set_caption('Pong')
        
        global game
        game = Game(speed=1, iteration=iteration)
        
        action = None
        
        hits = 0
        
        while game.wins < 7 and game.losses < 7 and game.hits < 1000000000: #main game loop
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    for button in game.settings.buttons.values():
                        if button.isClicked(event):
                            if button.name == "speed_down":
                                game.settings.updateSpeed(game.speed - 1)
                            elif button.name == "speed_up":
                                game.settings.updateSpeed(game.speed + 1)
                            elif button.name == "control":
                                game.settings.toggleControl(not user_controlled)
                            elif button.name == "lines":
                                game.settings.toggleLines(not visible)
                            elif button.name == "fps_down":
                                game.settings.updateFPS(fps - 50)
                            elif button.name == "fps_up":
                                game.settings.updateFPS(fps + 50)
                            elif button.name == "stats":
                                game.settings.toggleStats(not show_stats)
                        
            #User controls
            if user_controlled:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    game.paddles['user'].move(-1*game.speed)
                elif keys[pygame.K_DOWN]:
                    game.paddles['user'].move(game.speed)
            else:
                values = dict()
                values['last_action'] = action
                values['paddle_position'] = game.paddles['user'].rect.centery
                values['ball_y'] = game.ball.rect.centery
                values['ball_x'] = game.ball.rect.centerx
                throwaway, end_x, end_y = game.ball.path.getAbsoluteEnd()
                values['ball_end_x'] = end_x
                values['ball_end_y'] = end_y
                values['score'] = game.hits + game.wins - game.losses
                values['score_increased'] = hits < game.hits
                hits = game.hits
                
                action = wrapper.control(values)
                
                if action == 1:
                    game.paddles['user'].move(-1*game.speed)
                elif action == 0:
                    game.paddles['user'].move(game.speed)
            
            
            game.update()
            pygame.display.update()
            fps_clock.tick(fps)
        
            game.settings.saveSettings()
        wrapper.gameover(game.hits + (game.wins) - (game.losses))
            
            
#RunGame.run()