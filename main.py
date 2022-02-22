import ini_handler
import pygame
import random
import time
import os.path
import json
import os
import sys
import time

file_directory = __file__.split(os.path.sep)[:-1]

temp = ''
for i in file_directory:
    temp += i + os.path.sep

file_directory = temp[:-1]
del(temp)

#sys.path.append(file_directory) exe file only works with that
os.chdir(file_directory)

pygame.font.init()
pygame.init()

def write_text(text, size=24, color=(255,255,255), antialias=False, return_font=False):
    font = pygame.font.SysFont('', size)
    if return_font:
        return [font, font.render(str(text), antialias, color)]
    return font.render(str(text), antialias, color)

cfg = ini_handler.config('config.ini')
cfg.addconfig(1200,'WINDOW','width')
cfg.addconfig(600,'WINDOW','height')
cfg.addconfig('20,20,20','WINDOW','background_color')
cfg.addconfig('125,125,150','WINDOW','square_color')
cfg.addconfig('255,255,255','WINDOW','square_font_color')
cfg.addconfig(False, 'WINDOW', 'debug')
cfg.addconfig(15, 'WINDOW', 'debug_alpha')
cfg.addconfig(0.3, 'WINDOW', 'volume')

cfg.addconfig('default', 'MINESWEEPER', 'level')
cfg.addconfig(20,'MINESWEEPER','w_amount')
cfg.addconfig(15,'MINESWEEPER','h_amount')
cfg.addconfig(3, 'MINESWEEPER', 'lives')
cfg.addconfig(30, 'MINESWEEPER', 'bombs_amount')

cfg.addconfig('assets/flag.png','ASSETS','flag_image_path')
cfg.addconfig('assets/bomb.png','ASSETS','bomb_image_path')
cfg.addconfig('assets/lost.png', 'ASSETS', 'lost_image_path')

cfg.addconfig('assets/missed1.wav', 'ASSETS', 'missed_sound1')
cfg.addconfig('assets/missed2.wav', 'ASSETS', 'missed_sound2')
cfg.addconfig('assets/missed3.wav', 'ASSETS', 'missed_sound3')
cfg.addconfig('assets/missed4.wav', 'ASSETS', 'missed_sound4')
cfg.addconfig('assets/missed5.wav', 'ASSETS', 'missed_sound5')
cfg.addconfig('assets/lost.wav', 'ASSETS', 'lost_sound')
cfg.addconfig('assets/winning_sounds', 'ASSETS', 'winning_sounds_path')

cfg.getconfig()

cfg = cfg.returnresult()

level = cfg['MINESWEEPER']['level']
w_amount = cfg['MINESWEEPER']['w_amount']
h_amount = cfg['MINESWEEPER']['h_amount']
default_lives = cfg['MINESWEEPER']['lives']
bombs_amount = cfg['MINESWEEPER']['bombs_amount']

debug_mode = cfg['WINDOW']['debug']

if debug_mode:
    print(f'File path: {__file__}')
    
    level = input('level: ')
    debug_mode = False

levels = json.load(open('levels.json','r'))

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

w, h = cfg['WINDOW']['width'], cfg['WINDOW']['height']

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

background = cfg['WINDOW']['background_color'].split(',')
background = (int(background[0]), int(background[1]), int(background[2]))

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
else:
    lost_sound = None

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
del(size) # just to free memory

class Square(pygame.Rect):
    def __init__(self, screen, x: int, y: int, is_bomb: bool, color: tuple=(125,125,150)):
        width = GRID_W-3
        height = GRID_H-1
        super().__init__(x, y, width, height)
        
        self.screen = screen
        self.is_bomb = is_bomb
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
        
        if pygame.mouse.get_pressed()[0] and self.collidepoint(pygame.mouse.get_pos()):
            if self.is_bomb and not self.is_pressed:
                if not first_play:
                    self.lost = True
                    self.is_pressed = True
                    return -1
                else:
                    got_atleast_one = False
                    while not got_atleast_one:
                        square = random.choice(squares)
                        if square != self:
                            if not square.is_bomb and not square.is_pressed:
                                square.is_bomb = True
                                got_atleast_one = True
                        
                    if not got_atleast_one:
                        self.lost = True
                        self.is_pressed = True
                        return -1
                        
                    
                    remove_bomb(self, square)
                    
                    for square in squares:
                        square.bombs_nearby = square.check_bombs(bombs)
                    
                    self.get_zeros(squares)
                    self.is_pressed = True
                    first_play = False
                    return
            else:
                self.is_pressed = True
                self.get_zeros(squares)
                first_play = False
                return
        
        if pygame.mouse.get_pressed()[2] and self.collidepoint(pygame.mouse.get_pos()):
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
        squares.append(Square(SCREEN, x*GRID_W+2, y*GRID_H+1, False, square_color))

def remove_bomb(square: Square, replace_with: Square=None):
    square.is_bomb = False
    if not replace_with.is_bomb:
        replace_with.is_bomb = True
    if square in bombs:
        bombs.remove(square)
        if replace_with != None and replace_with not in bombs:
            bombs.append(replace_with)

def create_game():
    global bombs, already_started_counter, lives, first_play, lost
    
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
        
    bombs = bombs_arr
    return bombs_arr

class Games: # talvez fazer uma forma de mostrar como foi o jogo inteiro (pode usar uma array q adiciona cada bloco pressionado que foi negoçado e q foi bomba q ativou e pa ou sla)
    def __init__(self, filename):
        self.filename = filename
        
        if not os.path.exists(self.filename):
            with open(self.filename, 'w+') as f:
                f.write('{}')
        
        self.content = json.load(open(self.filename,'r'))
            
    def add_game(self, game_title: str, time: float, lives: int, default_lives: int, won_game: bool, bombs: int, grid_width: float, grid_height: float): # se lembrar de botar mais informação do jogo
        default_title = game_title
        index = 1
        for title in self.content:
            if title == game_title:
                game_title = default_title+str(index)
                index += 1
        
        self.content[game_title] = {
            'index':index,
            'time':time,
            'lives':lives,
            'default_lives':default_lives,
            'won':won_game,
            'bombs':bombs,
            'grid_width':grid_width,
            'grid_height':grid_height
        }

        json.dump(self.content, open(self.filename, 'w+'))

games = Games('games.json')

bombs = 0
create_game()

def start_new_game(won_game=True):
    global t_args, t_function, t_start, t_wanted, time_text, time_text_size, used_debug_mode, debug_mode

    gametime = str(time.time()-counter_start)
    gametime = gametime[:gametime.index('.')+2]
    
    if won_game:
        play_sound(random.choice(winning_sounds))

    out = f'Time: {gametime} Won: {str(won_game).lower()} Bombs: {len(bombs)}'
    
    time_text = write_text(out, int(WIDTH/30+HEIGHT/30), return_font=True)
    time_text_size = time_text[0].size(out)
    time_text = time_text[1]
    
    if not used_debug_mode:
        games.add_game('game', gametime, lives, default_lives, won_game, bombs_amount, GRID_W, GRID_H)
    else:
        debug_mode = False
        used_debug_mode = False
    
    t_start = pygame.time.get_ticks()
    t_wanted = 2500
    t_function = create_game
    t_args = []

counter_start = None
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

pressed_once = [False, False, False]

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

topbar_y_size = int(HEIGHT/10)
topbar_y = -topbar_y_size
topbar_desired_y = int(topbar_y_size/2)

game_title = write_text('SuadoSweeper', 32, square_color, return_font=True)
game_title_size = game_title[0].size('SuadoSweeper')
game_title = game_title[1]

square_surface = pygame.Surface((squares[0].width, squares[0].height))
square_surface.set_alpha(cfg['WINDOW']['debug_alpha'] if cfg['WINDOW']['debug_alpha'] >= 15 else 15)

missed_sounds_length = len(missed_sounds)
last_missed_sound = None
actual_missed_sound = None

lost = False
used_debug_mode = False
running = True
while running:
    if not first_play and not already_started_counter:
        counter_start = time.time()
        already_started_counter = True
    
    clock.tick(FPS)
    SCREEN.fill(background)
    
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
    if lost == False and keys[pygame.K_F3]:
        if pygame.K_F3 in released_keys and released_keys[pygame.K_F3] == True:
            debug_mode = not debug_mode
            used_debug_mode = True
        released_keys[pygame.K_F3] = False
    else:
        released_keys[pygame.K_F3] = True

    if lost == False and keys[pygame.K_ESCAPE]:
        if pygame.K_ESCAPE in released_keys and released_keys[pygame.K_ESCAPE] == True:
            draw_topbar = not draw_topbar
            released_keys[pygame.K_ESCAPE] = False
    else:
        released_keys[pygame.K_ESCAPE] = True

    for y in range(WIDTH):
        pygame.draw.line(SCREEN, (45,45,45), (y*GRID_W,0), (y*GRID_W,HEIGHT), 3)
    
    for x in range(HEIGHT):
        pygame.draw.line(SCREEN, (45,45,45), (0, x*GRID_H), (WIDTH, x*GRID_H))
    
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

        if t_start == -1 and square.update() == -1:
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
        SCREEN.blit(win_text, (WIDTH/2-win_text_size[0]/2,HEIGHT/2-win_text_size[1]/2))
        SCREEN.blit(time_text, (WIDTH/2-time_text_size[0]/2, HEIGHT/2+win_text_size[1]/2+5))
        if t_start == -1:
            start_new_game()

    if draw_topbar:
        if topbar_y < topbar_desired_y:
            topbar_y += topbar_desired_y/2
        if topbar_y > topbar_desired_y:
            topbar_y = topbar_desired_y
        
        flags_text = write_text(flags, num_size, return_font=True)
        flags_size = flags_text[0].size(str(flags))
        pygame.draw.line(SCREEN, background, (0,topbar_y), (WIDTH,topbar_y), topbar_y_size)
        SCREEN.blit(flag_image, (3,topbar_y/2))
        SCREEN.blit(flags_text[1], (GRID_W+6,topbar_y/2))
        SCREEN.blit(game_title, (WIDTH/2-game_title_size[0]/2,topbar_y/2))
    else:
        topbar_y = -40

    if lost:
        SCREEN.blit(lost_image, (WIDTH/4, HEIGHT/4))

    if t_start != -1 and pygame.time.get_ticks()-t_start >= t_wanted:
        t_start = -1
        t_function(*t_args)
    
    pressed_once = [False, False, False]
    pygame.display.update()

pygame.quit()