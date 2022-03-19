# WARNING: this code is messy and i'm lazy to make it better
import ini_handler
import pygame
import random
import time
import os.path
import json
import os
import time
import sys
from games_handler import *

file_directory = __file__.split(os.path.sep)[:-1]

temp = ''
for i in file_directory:
    temp += i + os.path.sep

file_directory = temp[:-1]
del(temp)

# I can't find a way to make os.chdir work when file is an executable
#os.chdir(file_directory)

pygame.font.init()
pygame.init()

cfg = ini_handler.config('config.ini')
cfg.addconfig(1200, 'WINDOW', 'width')
cfg.addconfig(600, 'WINDOW', 'height')
cfg.addconfig('255,255,255', 'WINDOW', 'default_font_color')
cfg.addconfig('20,20,20', 'WINDOW', 'background_color')
cfg.addconfig('40,40,40', 'WINDOW', 'button_color')
cfg.addconfig('125,125,150', 'WINDOW', 'square_color')
cfg.addconfig('255,255,255', 'WINDOW', 'square_font_color')
cfg.addconfig(15, 'WINDOW', 'debug_alpha')
cfg.addconfig(0.3, 'WINDOW', 'volume')
cfg.addconfig('45,45,45','WINDOW','grid_y_line_color')
cfg.addconfig('45,45,45','WINDOW','grid_x_line_color')
cfg.addconfig('games', 'WINDOW', 'games_path')

cfg.addconfig('default', 'MINESWEEPER', 'level')
cfg.addconfig(20,'MINESWEEPER','w_amount')
cfg.addconfig(15,'MINESWEEPER','h_amount')
cfg.addconfig(3, 'MINESWEEPER', 'lives')
cfg.addconfig(30, 'MINESWEEPER', 'bombs_amount')

cfg.addconfig('assets/flag.png','ASSETS','flag_image_path')
cfg.addconfig('assets/bomb.png','ASSETS','bomb_image_path')
cfg.addconfig('assets/lost.png', 'ASSETS', 'lost_image_path')
cfg.addconfig('assets/click.mp3', 'ASSETS', 'click_sound')
cfg.addconfig('assets/lost.wav', 'ASSETS', 'lost_sound')
cfg.addconfig('assets/missed1.wav', 'ASSETS', 'missed_sound1')
cfg.addconfig('assets/missed2.wav', 'ASSETS', 'missed_sound2')
cfg.addconfig('assets/missed3.wav', 'ASSETS', 'missed_sound3')
cfg.addconfig('assets/missed4.wav', 'ASSETS', 'missed_sound4')
cfg.addconfig('assets/missed5.wav', 'ASSETS', 'missed_sound5')
cfg.addconfig('assets/winning_sounds', 'ASSETS', 'winning_sounds_path')

cfg.addconfig('ESCAPE', 'BINDS', 'topbar_toggle')
cfg.addconfig('F3', 'BINDS', 'debug_mode')
cfg.addconfig('F5', 'BINDS', 'reload_game')

cfg.addconfig(170, 'TOPBAR', 'background_alpha')
cfg.addconfig('20,20,20', 'TOPBAR', 'background_color')
cfg.addconfig('100,0,0', 'TOPBAR', 'lives_font_color')
cfg.addconfig('125,125,150','TOPBAR', 'gametitle_color')
cfg.addconfig('255,255,255', 'TOPBAR', 'flags_font_color')
cfg.addconfig('255,255,255', 'TOPBAR', 'time_font_color')

cfg.getconfig()
cfg = cfg.returnresult()

default_color = cfg['WINDOW']['default_font_color'].split(',')
default_color = (int(default_color[0]), int(default_color[1]), int(default_color[2]))

games_path = cfg['WINDOW']['games_path']
if games_path.endswith(os.sep):
    games_path = games_path[:-1]

def write_text(text, size=24, color=default_color, antialias=False, return_font=False):
    font = pygame.font.SysFont('', size)
    if return_font:
        return [font, font.render(str(text), antialias, color)]
    return font.render(str(text), antialias, color)

topbar_key = cfg['BINDS']['topbar_toggle']
topbar_key = eval(f'pygame.K_{topbar_key}')

debug_mode_key = cfg['BINDS']['debug_mode']
debug_mode_key = eval(f'pygame.K_{debug_mode_key}')

reload_game_key = cfg['BINDS']['reload_game']
reload_game_key = eval(f'pygame.K_{reload_game_key}')

level = cfg['MINESWEEPER']['level']
w_amount = cfg['MINESWEEPER']['w_amount']
h_amount = cfg['MINESWEEPER']['h_amount']
default_lives = cfg['MINESWEEPER']['lives']
bombs_amount = cfg['MINESWEEPER']['bombs_amount']

w, h = None, None
args = sys.argv[1:]
ignore_indexes = []
for index,arg in enumerate(args):
    if index not in ignore_indexes:
        if arg == '-level':
            ignore_indexes.append(index+1)
            if len(args)-1 > index:
                level = args[index+1]
        
        elif arg == '-load' and '-watch' not in args:
            if len(args)-1 > index+1: # index+1 for 2 args
                ignore_indexes.append(index+1)
                ignore_indexes.append(index+2)
                #args[index+1] # filename
                #args[index+2] # gametitle
        
        elif arg == '-watch':
            if len(args)-1 > index+1: # index+1 for 2 args
                ignore_indexes.append(index+1)
                ignore_indexes.append(index+2)
                #args[index+1] # filename
                #args[index+2] # gametitle
        elif arg == '-w' or arg == '-width':
            if len(args)-1 > index:
                ignore_indexes.append(index+1)
                w = int(args[index+1])
        elif arg == '-h' or arg == '-height':
            if len(args)-1 > index:
                ignore_indexes.append(index+1)
                h = int(args[index+1])
        else:
            print(f'Unknown command: {arg}')
del(ignore_indexes)

levels = json.load(open('levels.json','r'))

def get_level():
    global w_amount, h_amount, bombs_amount, default_lives
    for l in levels:
        if level in l.replace(' ','').split(';'):
            l = levels[l]
            w_amount = l['w_amount']
            h_amount = l['h_amount']
            bombs_amount = l['bombs_amount']
            default_lives = l['lives']
            break
    
    if bombs_amount >= w_amount*h_amount:
        bombs_amount = w_amount*h_amount-1

get_level()

if w == None:
    w = cfg['WINDOW']['width']
if h == None:
    h = cfg['WINDOW']['height']

if w < 400:
    w = 400
if h < 400:
    h = 400
if w > 1300:
    w = 1300
if h > 800:
    h = 800

WIDTH, HEIGHT = w, h
del(w)
del(h)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('DemoSweeper')
if os.path.exists('icon.png'):
    pygame.display.set_icon(pygame.transform.scale(pygame.image.load('icon.png'), (150,150)))

lives = default_lives

clock = pygame.time.Clock()
FPS = 60

GRID_W = int(WIDTH/w_amount)
GRID_H = int(HEIGHT/h_amount)

grid_x_line_color = cfg['WINDOW']['grid_x_line_color'].split(',')
grid_x_line_color = (int(grid_x_line_color[0]), int(grid_x_line_color[1]), int(grid_x_line_color[2]))

grid_y_line_color = cfg['WINDOW']['grid_y_line_color'].split(',')
grid_y_line_color = (int(grid_y_line_color[0]), int(grid_y_line_color[1]), int(grid_y_line_color[2]))

background = cfg['WINDOW']['background_color'].split(',')
background = (int(background[0]), int(background[1]), int(background[2]))

button_color = cfg['WINDOW']['button_color'].split(',')
button_color = (int(button_color[0]), int(button_color[1]), int(button_color[2]))

topbar_background = cfg['TOPBAR']['background_color'].split(',')
topbar_background = (int(topbar_background[0]), int(topbar_background[1]), int(topbar_background[2]))

topbar_lives_font_color = cfg['TOPBAR']['lives_font_color'].split(',')
topbar_lives_font_color = (int(topbar_lives_font_color[0]), int(topbar_lives_font_color[1]), int(topbar_lives_font_color[2]))

topbar_gametitle_color = cfg['TOPBAR']['gametitle_color'].split(',')
topbar_gametitle_color = (int(topbar_gametitle_color[0]), int(topbar_gametitle_color[1]), int(topbar_gametitle_color[2]))

topbar_flags_font_color = cfg['TOPBAR']['flags_font_color'].split(',')
topbar_flags_font_color = (int(topbar_flags_font_color[0]), int(topbar_flags_font_color[1]), int(topbar_flags_font_color[2]))

topbar_time_font_color = cfg['TOPBAR']['time_font_color'].split(',')
topbar_time_font_color = (int(topbar_time_font_color[0]), int(topbar_time_font_color[1]), int(topbar_time_font_color[2]))

flag_image = pygame.transform.scale(pygame.image.load(cfg['ASSETS']['flag_image_path']), (GRID_W-3,GRID_H-1))
bomb_image = pygame.transform.scale(pygame.image.load(cfg['ASSETS']['bomb_image_path']), (GRID_W-3,GRID_H-1))
lost_image = pygame.transform.scale(pygame.image.load(cfg['ASSETS']['lost_image_path']), (WIDTH/2, HEIGHT/2))

volume = cfg['WINDOW']['volume']
def play_sound(sound: str | pygame.mixer.Sound, wait_end: bool=False, fade_ms: int=0):
    if type(sound) != pygame.mixer.Sound:
        sound = pygame.mixer.Sound(sound)
        sound.set_volume(volume)
    
    sound.play(fade_ms=fade_ms)
    if wait_end == False:
        return
    
    t_start = time.time()
    while time.time()-t_start < sound.get_length():
            continue

if os.path.exists(cfg['ASSETS']['lost_sound']): 
    lost_sound = pygame.mixer.Sound(cfg['ASSETS']['lost_sound'])
    lost_sound.set_volume(volume)
else:
    lost_sound = None

click_sound = cfg['ASSETS']['click_sound']
if os.path.exists(click_sound):
    click_sound = pygame.mixer.Sound(click_sound)
    click_sound.set_volume(volume)
else:
    click_sound = None

missed_sounds = []
for i in range(5):
    sound = cfg['ASSETS'][f'missed_sound{i+1}']
    if os.path.exists(sound):
        missed_sounds.append(pygame.mixer.Sound(sound))
        missed_sounds[-1].set_volume(volume)

winning_sounds_path = cfg['ASSETS']['winning_sounds_path']
winning_sounds = []
if os.path.exists(winning_sounds_path):
    for i in os.listdir(winning_sounds_path):
        if i.endswith('.wav') or i.endswith('.mp3'):
            winning_sounds.append(pygame.mixer.Sound(winning_sounds_path+os.path.sep+i))
            winning_sounds[-1].set_volume(volume)

del(winning_sounds_path)

square_color = cfg['WINDOW']['square_color'].split(',')
square_color = (int(square_color[0]), int(square_color[1]), int(square_color[2]))

square_font_color = cfg['WINDOW']['square_font_color'].split(',')
square_font_color = (int(square_font_color[0]), int(square_font_color[1]), int(square_font_color[2]))

numbers = []
num_size = int(WIDTH/30)
if num_size < 16:
    num_size = 16

for num in range(9):
    font, text = write_text(num, num_size, square_font_color, return_font=True)
    size = font.size(str(num))
    numbers.append([size, text])

del(num)
del(size) # just to free memory...

game_actions = {}
game_squares = []

class Square(pygame.Rect):
    def __init__(self, screen, x: int, y: int, is_bomb: bool, index: int, color: tuple=(125,125,150)):
        width = GRID_W-3
        height = GRID_H-1
        super().__init__(x, y, width, height)
        
        self.screen = screen
        self.is_bomb = is_bomb
        self.index = index
        self.color = color

        self.is_pressed = False
        self.flag_color = background
        self.bomb_color = (100,25,25)
        self.lost = False
        self.last_tick = 0
        self.is_flag = False
        
        self.bombs_nearby = numbers[0]

    def check_bombs(self, bombs):
        if self.is_bomb:
            return
        
        out = 0
        for bomb in bombs:
            if bomb.y == self.y: # center
                if bomb.x == self.x-self.width-3:
                    out += 1
                elif bomb.x == self.x+self.width+3:
                    out += 1
            elif bomb.y == self.y-self.height-1: # up
                if bomb.x == self.x-self.width-3: # left
                    out += 1
                elif bomb.x == self.x: # center
                    out += 1
                elif bomb.x == self.x+self.width+3: # right
                    out += 1
            elif bomb.y == self.y+self.height+1: # down
                if bomb.x == self.x: # center
                    out += 1
                elif bomb.x == self.x-self.width-3: # left
                    out += 1
                elif bomb.x == self.x+self.width+3: # right
                    out += 1
        
        return numbers[out]

    def update(self):
        global first_play
        
        if self.is_pressed and not self.is_bomb and not self.is_flag:
            return
        
        if pygame.mouse.get_pressed()[0] and self.collidepoint(pygame.mouse.get_pos()) and not self.is_flag:
            game_actions['mouse1'].append([pygame.time.get_ticks(), self.index])

            if self.is_bomb and not self.is_pressed:
                if not first_play:
                    self.lost = True
                    self.is_pressed = True
                    return -1
                else:
                    replaced_one = False
                    while not replaced_one:
                        square = random.randint(0,len(squares)-1)
                        if squares[square] != self:
                            if not squares[square].is_bomb and not squares[square].is_pressed:
                                squares[square].is_bomb = True
                                game_squares[self.index] = False
                                game_squares[square] = True
                                replaced_one = True
                        
                    if not replaced_one:
                        self.lost = True
                        self.is_pressed = True
                        return -1
                        
                    
                    remove_bomb(self, squares[square])
                    
                    for square in squares:
                        square.bombs_nearby = square.check_bombs(bombs)
                    
                    self.get_zeros(squares)
                    self.is_pressed = True
                    first_play = False
                    play_sound(click_sound)
                    return
            else:
                self.is_pressed = True
                self.get_zeros(squares)
                first_play = False
                play_sound(click_sound)
                return
        
        if pygame.mouse.get_pressed()[2] and self.collidepoint(pygame.mouse.get_pos()):
            game_actions['mouse2'].append([pygame.time.get_ticks(), self.index])

            if pygame.time.get_ticks()-self.last_tick > 325:
                self.is_pressed = not self.is_pressed
                self.last_tick = pygame.time.get_ticks()
                self.is_flag = not self.is_flag
            return
                
    def draw(self):
        if not self.is_pressed:
            return
        
        if self.is_flag:
            pygame.draw.rect(self.screen, self.flag_color, self)
            self.screen.blit(flag_image, (self.x, self.y))
        elif self.is_bomb:
            if self.lost:
                pygame.draw.rect(self.screen, self.bomb_color, self)
                self.screen.blit(bomb_image, (self.x, self.y))
        else:
            pygame.draw.rect(self.screen, self.color, self)
            self.screen.blit(self.bombs_nearby[1], (self.centerx-self.bombs_nearby[0][0]/2, self.centery-self.bombs_nearby[0][1]/2))

    def get_zeros(self, squares):
        if self.bombs_nearby != numbers[0]:
            return
        
        for square in squares:
            if square != self and not square.is_bomb and not square.is_pressed and not square.is_flag:
                if square.x == self.x-square.width-3 or square.x == self.x+square.width+3 or self.x == square.x:
                    if square.y == self.y-square.height-1 or square.y == self.y or square.y == self.y+square.height+1:
                        square.is_pressed = True
                        if square.bombs_nearby == numbers[0]:
                            square.get_zeros(squares)

squares = []
for y in range(h_amount): # pygame.draw.line(SCREEN, background, (0,20), (WIDTH,20), 40)
    for x in range(w_amount):
        squares.append(Square(SCREEN, x*GRID_W+2, y*GRID_H+1, False, len(squares), square_color))

def remove_bomb(square: Square, replace_with: Square=None):
    square.is_bomb = False
    if not replace_with.is_bomb:
        replace_with.is_bomb = True
    if square in bombs:
        bombs.remove(square)
        if replace_with != None and replace_with not in bombs:
            bombs.append(replace_with)

def create_game():
    global bombs, already_started_counter, lives, first_play, lost, counter_start, game_actions, game_squares
    
    game_actions = {'debug_mode_key':[],'topbar_key':[],'reload_game_key':[],'mouse1':[],'mouse2':[]}

    game_squares = []
    counter_start = None

    lost = False

    first_play = True
    already_started_counter = False
    lives = default_lives
    
    for square in squares:
        square.is_bomb = False
        square.is_pressed = False
        square.lost = False
        square.is_flag = False

    bombs_arr = []
    bombs = 0
    while bombs != bombs_amount:
        square = random.choice(squares)
        if not square.is_bomb:
            square.is_bomb = True
            bombs_arr.append(square)
            bombs += 1
    
    for square in squares:
        square.bombs_nearby = square.check_bombs(bombs_arr)
        game_squares.append(square.is_bomb)
        
    bombs = bombs_arr
    return bombs_arr

bombs = None # bombs = bombs_arr -> type(bombs) = list
create_game()

def start_new_game(won_game=True, wait_time=2500):
    global t_args, t_function, t_start, t_wanted, time_text, time_text_size, used_debug_mode, debug_mode

    gametime = str(time.time()-counter_start)
    gametime = gametime[:gametime.index('.')+2]
    
    if won_game:
        play_sound(random.choice(winning_sounds))

    out = f'Time: {gametime} Bombs: {len(bombs)}'
    
    time_text = write_text(out, int(WIDTH/30+HEIGHT/30), return_font=True)
    time_text_size = time_text[0].size(out)
    time_text = time_text[1]
    
    if not used_debug_mode:
        game = Game(games_path+os.sep+'game.json')
        game.add_game(gametime, default_lives, won_game, bombs_amount, w_amount, h_amount, WIDTH, HEIGHT, game_actions, game_squares)
    else:
        debug_mode = False
        used_debug_mode = False
    
    t_start = pygame.time.get_ticks()
    t_wanted = wait_time
    t_function = create_game
    t_args = []

def restart_game():
    global lives
    lives -= 1
    
    if lives == 0:
        start_new_game(False)
        return

    for square in squares:
        if square.is_bomb and square.is_pressed and not square.is_flag:
            square.is_pressed = False
        
        square.lost = False

def ignore_func():
    pass

pressed_once = [False, False, False]

debug_mode = False

t_start = -1
t_wanted = 0
t_function = None
t_args = []

win_text = write_text('SPY WON', int(WIDTH/10+HEIGHT/5), return_font=True)
win_text_size = win_text[0].size('SPY WON')
win_text = win_text[1]

time_text = write_text('', 1, return_font=True)
time_text_size = time_text[0].size('')
time_text = time_text[1]

first_play = True # pode mudar o nome, ta bem bosta
already_started_counter = False # aq tb pode mudar

draw_topbar = False
released_keys = {}

topbar = pygame.Surface((WIDTH, int(HEIGHT/10)))
topbar.set_alpha(cfg['TOPBAR']['background_alpha'])

topbar_y_size = topbar.get_height()
topbar_y = -topbar_y_size
topbar_desired_y = 0

game_title = write_text('DemoSweeper', 32, topbar_gametitle_color, return_font=True)
game_title_size = game_title[0].size('DemoSweeper')
game_title = game_title[1]

square_surface = pygame.Surface((squares[0].width, squares[0].height))
square_surface.set_alpha(cfg['WINDOW']['debug_alpha'] if cfg['WINDOW']['debug_alpha'] >= 15 else 15)

missed_sounds_length = len(missed_sounds)
last_missed_sound = None
actual_missed_sound = None

# rg stands for restart game
rg_request_draw = False

rg_request_text = write_text('restart?', num_size, (255,0,0), return_font=True)
rg_request_size = rg_request_text[0].size('restart?')
rg_request_text = rg_request_text[1]

rg_request_box = pygame.Rect(WIDTH/4,HEIGHT/4, WIDTH/2,HEIGHT/2)

rg_request_yes_text = write_text('yes', num_size, return_font=True)
rg_request_yes_text_size = rg_request_yes_text[0].size('yes')
rg_request_yes_text = rg_request_yes_text[1]
rg_request_yesbutton = pygame.Rect(rg_request_box.x+25,rg_request_box.y+rg_request_box.height-65,rg_request_yes_text_size[0]+10,rg_request_yes_text_size[1]+5)

rg_request_no_text = write_text('no', num_size, return_font=True)
rg_request_no_text_size = rg_request_no_text[0].size('no')
rg_request_no_text = rg_request_no_text[1]
rg_request_nobutton = pygame.Rect(rg_request_box.x+rg_request_box.width-75,rg_request_box.y+rg_request_box.height-65,rg_request_no_text_size[0]+10,rg_request_no_text_size[1]+5)

topbar_flag_image = pygame.transform.scale(flag_image, (WIDTH/30,-topbar_y/2))

counter_start = None
lost = False
used_debug_mode = False
running = True
while running:
    clock.tick(FPS)
    SCREEN.fill(background)
    
    if not first_play and not already_started_counter:
        counter_start = time.time()
        already_started_counter = True
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pressed_once[0] = True
            elif event.button == 2:
                pressed_once[1] = True
            else:
                pressed_once[2] = True
    
    keys = pygame.key.get_pressed()
    if lost == False and keys[debug_mode_key]:
        if debug_mode_key in released_keys and released_keys[debug_mode_key] == True:
            debug_mode = not debug_mode
            used_debug_mode = True
            game_actions['debug_mode_key'].append(pygame.time.get_ticks())
        released_keys[debug_mode_key] = False
    else:
        released_keys[debug_mode_key] = True

    if lost == False and keys[topbar_key]:
        if topbar_key in released_keys and released_keys[topbar_key] == True:
            draw_topbar = not draw_topbar
            released_keys[topbar_key] = False
            game_actions['topbar_key'].append(pygame.time.get_ticks())
    else:
        released_keys[topbar_key] = True

    if lost == False and keys[reload_game_key]:
        if reload_game_key in released_keys and released_keys[reload_game_key] == True:
            rg_request_draw = not rg_request_draw
            released_keys[reload_game_key] = False
            game_actions['reload_game_key'].append(pygame.time.get_ticks())
    else:
        released_keys[reload_game_key] = True

    for x in range(WIDTH): # | | | |
        pygame.draw.line(SCREEN, grid_x_line_color, (x*GRID_W,0), (x*GRID_W,HEIGHT), 3)
    
    for y in range(HEIGHT): # -------
        pygame.draw.line(SCREEN, grid_y_line_color, (0, y*GRID_H), (WIDTH, y*GRID_H))
    
    flags = len(bombs)
    correct = 0
    for square in squares:
        square.draw()

        if debug_mode:
            if square.is_bomb:
                square_surface.fill((255,0,0))
                SCREEN.blit(square_surface, (square.x, square.y))
            else:
                square_surface.fill((0,255,0))
                SCREEN.blit(square_surface, (square.x, square.y))

        if t_start == -1 and rg_request_draw == False and square.update() == -1:
            if lives == 1:
                if lost_sound != None:
                    play_sound(lost_sound)
                lost = True
            elif missed_sounds_length != 0:
                if missed_sounds_length > 1:
                    while actual_missed_sound == last_missed_sound:
                        actual_missed_sound = random.choice(missed_sounds)
                    last_missed_sound = actual_missed_sound
                    play_sound(actual_missed_sound)
                else:
                    play_sound(missed_sounds[0])
            
            t_start = pygame.time.get_ticks()
            t_wanted = 1000
            t_function = restart_game
            t_args = []
        if square.is_flag:
            if square.is_bomb:
                correct += 1
            flags -= 1

        elif square.is_pressed and not square.is_flag and not square.is_bomb:
            correct += 1
    
    if correct == len(squares):
        if t_start == -1:
            start_new_game()
        SCREEN.blit(win_text, (WIDTH/2-win_text_size[0]/2,HEIGHT/2-win_text_size[1]/2))
        SCREEN.blit(time_text, (WIDTH/2-time_text_size[0]/2, HEIGHT/2+win_text_size[1]/2+5))

    if draw_topbar:
        if topbar_y < topbar_desired_y:
            topbar_y += topbar_y_size/6
        if topbar_y > topbar_desired_y:
            topbar_y = topbar_desired_y
        
        flags_text = write_text(flags, num_size, topbar_flags_font_color, return_font=True)
        flags_size = flags_text[0].size(str(flags))
        
        SCREEN.blit(topbar, (0,topbar_y))
        topbar.fill(topbar_background)
        topbar.blit(topbar_flag_image, (3,topbar.get_height()/3))
        topbar.blit(flags_text[1], (topbar_flag_image.get_rect().width+6,topbar.get_height()/3))
        topbar.blit(game_title, (WIDTH/2-game_title_size[0]/2,topbar.get_height()/3))

        lives_text = write_text(f'Lives: {str(lives)}', num_size, topbar_lives_font_color, return_font=True)
        lives_text_size = lives_text[0].size(f'Lives: {str(lives)}')
        lives_text = lives_text[1]
        topbar.blit(lives_text, (WIDTH/2+game_title_size[0]/2+lives_text_size[0], topbar.get_height()/3))
        
        if counter_start != None and correct != len(squares):
            gametime = str(time.time()-counter_start)
            gametime = gametime[:gametime.index('.')+2]
            time_text = write_text(gametime, num_size, topbar_time_font_color, return_font=True)
            time_text_size = time_text[0].size(gametime)
            time_text = time_text[1]
            topbar.blit(time_text, (topbar.get_width()-time_text_size[0],topbar.get_height()/3))
    else:
        topbar_y = -topbar_y_size

    if lost:
        SCREEN.blit(lost_image, (WIDTH/4, HEIGHT/4))

    if rg_request_draw:
        pygame.draw.rect(SCREEN, background, rg_request_box)
        
        SCREEN.blit(rg_request_text, (rg_request_box.x+(rg_request_box.width/2)-(rg_request_size[0]/2), rg_request_box.y+(rg_request_box.height/2)-(rg_request_size[1]/2)))

        pygame.draw.rect(SCREEN, button_color, rg_request_yesbutton)
        SCREEN.blit(rg_request_yes_text, (rg_request_yesbutton.x+(rg_request_yesbutton.width/2)-(rg_request_yes_text_size[0]/2), rg_request_yesbutton.y+(rg_request_yesbutton.height/2)-(rg_request_yes_text_size[1]/2)))

        pygame.draw.rect(SCREEN, button_color, rg_request_nobutton)
        SCREEN.blit(rg_request_no_text, (rg_request_nobutton.x+(rg_request_nobutton.width/2)-(rg_request_no_text_size[0]/2), rg_request_nobutton.y+(rg_request_nobutton.height/2)-(rg_request_no_text_size[1]/2)))

        if rg_request_yesbutton.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            used_debug_mode = True
            rg_request_draw = False
            counter_start = 0
            start_new_game(False, 150)
        elif rg_request_nobutton.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            rg_request_draw = False
            t_start = pygame.time.get_ticks()
            t_function = ignore_func
            t_wanted = 150

    if t_start != -1 and pygame.time.get_ticks()-t_start >= t_wanted:
        t_start = -1
        t_function(*t_args)
    
    pressed_once = [False, False, False]
    pygame.display.update()

pygame.quit()