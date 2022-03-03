# WARNING: this code is messy and i'm lazy to make it better
from distutils.errors import UnknownFileError
import pygame
import json
import os
import sys
import ini_handler
import time
import random

pygame.init()
pygame.font.init()

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
                    play_sound(click_sound)
                    return
            else:
                self.is_pressed = True
                self.get_zeros(squares)
                first_play = False
                play_sound(click_sound)
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

bombs = []
def remove_bomb(square: Square, replace_with: Square=None):
    square.is_bomb = False
    if not replace_with.is_bomb:
        replace_with.is_bomb = True
    if square in bombs:
        bombs.remove(square)
        if replace_with != None and replace_with not in bombs:
            bombs.append(replace_with)

class GameLoader:
    def __init__(self, width: int, height: int, filename: str, gametitle: str=None):
        self.running = False
        self.gametitle = gametitle
        self.content = self.load(filename, self.gametitle)
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.background = (0,0,0)
        self.pressed_once = [False, False, False]
        pygame.display.set_caption('GameReader')
        if os.path.exists('icon.png'):
            pygame.display.set_icon(pygame.transform.scale(pygame.image.load('icon.png'), (150,150)))
    
    def load(self, filename: str, gametitle: str=None):
        if not os.path.exists(filename):
            raise UnknownFileError(f'File {filename} does not exists')
        
        filecontent = json.load(open(filename,'r'))
        if gametitle == None:
            content = filecontent
            return
        
        if str(gametitle) in filecontent:
            content = filecontent[gametitle]
        else:
            raise KeyError(f'{gametitle} not in {filename}')
        return content

    def play(self):
        global restart_game, lost, t_start, t_args, t_function, t_wanted, lives, counter_start, already_started_counter, debug_mode, draw_topbar, rg_request_draw
        
        for square in squares:
            square.draw()
            square.update()
        
        if not first_play and not already_started_counter:
            counter_start = time.time()
            already_started_counter = True
        
        keys = pygame.key.get_pressed()
        if lost == False and keys[debug_mode_key]:
            if debug_mode_key in released_keys and released_keys[debug_mode_key] == True:
                debug_mode = not debug_mode
            released_keys[debug_mode_key] = False
        else:
            released_keys[debug_mode_key] = True

        if lost == False and keys[quick_menu_key]:
            if quick_menu_key in released_keys and released_keys[quick_menu_key] == True:
                draw_topbar = not draw_topbar
                released_keys[quick_menu_key] = False
        else:
            released_keys[quick_menu_key] = True

        if lost == False and keys[reload_game_key]:
            if reload_game_key in released_keys and released_keys[reload_game_key] == True:
                rg_request_draw = not rg_request_draw
                released_keys[reload_game_key] = False
        else:
            released_keys[reload_game_key] = True

        flags = len(bombs)
        correct = 0
        for square in squares:
            square.draw()

        if debug_mode:
            if square.is_bomb:
                square_surface.fill((255,0,0))
                self.screen.blit(square_surface, (square.x, square.y))
            else:
                square_surface.fill((0,255,0))
                self.screen.blit(square_surface, (square.x, square.y))

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
            self.screen.blit(win_text, (self.width/2-win_text_size[0]/2,self.height/2-win_text_size[1]/2))
            self.screen.blit(time_text, (self.width/2-time_text_size[0]/2, self.height/2+win_text_size[1]/2+5))

        if draw_topbar:
            if topbar_y < topbar_desired_y:
                topbar_y += topbar_desired_y/2
            if topbar_y > topbar_desired_y:
                topbar_y = topbar_desired_y
            
            flags_text = write_text(flags, num_size, return_font=True)
            flags_size = flags_text[0].size(str(flags))
            pygame.draw.line(self.screen, background, (0,topbar_y), (self.width,topbar_y), topbar_y_size)
            self.screen.blit(topbar_flag_image, (3,topbar_y/2))
            self.screen.blit(flags_text[1], (topbar_flag_image.get_rect().width+6,topbar_y/2))
            self.screen.blit(game_title, (self.width/2-game_title_size[0]/2,topbar_y/2))

            lives_text = write_text(f'Lives: {str(lives)}', num_size, (100,0,0), return_font=True)
            lives_text_size = lives_text[0].size(f'Lives: {str(lives)}')
            lives_text = lives_text[1]
            self.screen.blit(lives_text, (self.width/2+game_title_size[0]/2+lives_text_size[0], topbar_y/2))
            
            if counter_start != None and correct != len(squares):
                gametime = str(time.time()-counter_start)
                gametime = gametime[:gametime.index('.')+2]
                time_text = write_text(gametime, num_size, return_font=True)
                time_text_size = time_text[0].size(gametime)
                time_text = time_text[1]
                self.screen.blit(time_text, (self.width-time_text_size[0]-5,topbar_y/2))
        else:
            topbar_y = -topbar_y_size

        if lost:
            self.screen.blit(lost_image, (self.width/4, self.height/4))

        if rg_request_draw:
            pygame.draw.rect(self.screen, background, rg_request_box)
            
            self.screen.blit(rg_request_text, (rg_request_box.x+(rg_request_box.width/2)-(rg_request_size[0]/2), rg_request_box.y+(rg_request_box.height/2)-(rg_request_size[1]/2)))

            pygame.draw.rect(self.screen, button_color, rg_request_yesbutton)
            self.screen.blit(rg_request_yes_text, (rg_request_yesbutton.x+(rg_request_yesbutton.width/2)-(rg_request_yes_text_size[0]/2), rg_request_yesbutton.y+(rg_request_yesbutton.height/2)-(rg_request_yes_text_size[1]/2)))

            pygame.draw.rect(self.screen, button_color, rg_request_nobutton)
            self.screen.blit(rg_request_no_text, (rg_request_nobutton.x+(rg_request_nobutton.width/2)-(rg_request_no_text_size[0]/2), rg_request_nobutton.y+(rg_request_nobutton.height/2)-(rg_request_no_text_size[1]/2)))

            if rg_request_yesbutton.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                used_debug_mode = True
                rg_request_draw = False
                counter_start = 0

            if rg_request_nobutton.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                rg_request_draw = False

        if t_start != -1 and pygame.time.get_ticks()-t_start >= t_wanted:
            t_start = -1
            t_function(*t_args)
        
        pressed_once = [False, False, False]

    def watch(self):
        for square in squares:
            square.draw()
    
    def mainloop(self, mode: str='play'): # 'play' or 'watch' only.
        if mode == 'play':
            func = self.play
        elif mode == 'watch':
            func = self.watch
        else:
            raise TypeError(f'Unknown mode \'{mode}\'.')
        
        self.running = True
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill(self.background)

            for y in range(self.width):
                pygame.draw.line(self.screen, (45,45,45), (y*GRID_W,0), (y*GRID_W,self.height), 3)
    
            for x in range(self.height):
                pygame.draw.line(self.screen, (45,45,45), (0, x*GRID_H), (self.width, x*GRID_H))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.pressed_once[0] = True
                    elif event.button == 2:
                        self.pressed_once[1] = True
                    else:
                        self.pressed_once[2] = True

            func()

            pygame.display.update()

if __name__ == '__main__':
    file_directory = __file__.split(os.path.sep)[:-1]

    temp = ''
    for i in file_directory:
        temp += i + os.path.sep

    file_directory = temp[:-1]
    del(temp)
    
    #sys.path.append(file_directory) # exe file only works with that instead of os.chdir
    os.chdir(file_directory)

    cfg = ini_handler.config('config.ini')
    cfg.getconfig()
    cfg = cfg.returneverything()
    args = sys.argv[1:]
    argss = [int(cfg['WINDOW']['width']),int(cfg['WINDOW']['height'])]
    
    if len(args) == 0:
        raise IndexError('Expected at least filename argument.')
    
    argss.append(args[0])
    if len(args) >= 2:
        argss.append(args[1])
    
    game = GameLoader(*argss)
    del(argss)
    del(args)
    
    background = cfg['WINDOW']['background_color'].split(',')
    background = (int(background[0]), int(background[1]), int(background[2]))
    game.background = background

    def write_text(text, size=24, color=(255,255,255), antialias=False, return_font=False):
        font = pygame.font.SysFont('', size)
        if return_font:
            return [font, font.render(str(text), antialias, color)]
        return font.render(str(text), antialias, color)

    button_color = cfg['WINDOW']['button_color'].split(',')
    button_color = (int(button_color[0]), int(button_color[1]), int(button_color[2]))

    w_amount = game.content['grid_w_amount']
    h_amount = game.content['grid_h_amount']

    GRID_W = int(game.width/w_amount)
    GRID_H = int(game.height/h_amount)

    flag_image = pygame.transform.scale(pygame.image.load(cfg['ASSETS']['flag_image_path']), (GRID_W-3,GRID_H-1))
    bomb_image = pygame.transform.scale(pygame.image.load(cfg['ASSETS']['bomb_image_path']), (GRID_W-3,GRID_H-1))
    lost_image = pygame.transform.scale(pygame.image.load(cfg['ASSETS']['lost_image_path']), (game.width/2, game.height/2))

    volume = float(cfg['WINDOW']['volume'])
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
    num_size = int(game.width/30)
    if num_size < 16:
        num_size = 16

    for num in range(9):
        font, text = write_text(num, num_size, square_font_color, return_font=True)
        size = font.size(str(num))
        numbers.append([size, text])

    del(num)
    del(size) # just to free memory...

    squares = []
    for y in range(h_amount): # pygame.draw.line(self.screen, background, (0,20), (game.width,20), 40)
        for x in range(w_amount):
            squares.append(Square(game.screen, x*GRID_W+2, y*GRID_H+1, False, len(squares), square_color))
            squares[-1].is_bomb = game.content['squares'][len(squares)-1]

    for square in squares:
        square.bombs_nearby = square.check_bombs(bombs)

    pressed_once = [False, False, False]

    debug_mode = False

    t_start = -1
    t_wanted = 0
    t_function = None
    t_args = []

    win_text = write_text('SPY WON', int(game.width/10+game.height/5), return_font=True)
    win_text_size = win_text[0].size('SPY WON')
    win_text = win_text[1]

    time_text = write_text('', 1, return_font=True)
    time_text_size = time_text[0].size('')
    time_text = time_text[1]

    first_play = True # pode mudar o nome, ta bem bosta
    already_started_counter = False # aq tb pode mudar

    draw_topbar = False
    released_keys = {}

    topbar_y_size = int(game.height/10)
    topbar_y = -topbar_y_size
    topbar_desired_y = int(topbar_y_size/2)

    game_title = write_text('SuadoSweeper', 32, square_color, return_font=True)
    game_title_size = game_title[0].size('SuadoSweeper')
    game_title = game_title[1]

    square_surface = pygame.Surface((squares[0].width, squares[0].height))
    square_surface.set_alpha(int(cfg['WINDOW']['debug_alpha']) if int(cfg['WINDOW']['debug_alpha']) >= 15 else 15)

    missed_sounds_length = len(missed_sounds)
    last_missed_sound = None
    actual_missed_sound = None

    # rg stands for restart game
    rg_request_draw = False

    rg_request_text = write_text('restart?', num_size, (255,0,0), return_font=True)
    rg_request_size = rg_request_text[0].size('restart?')
    rg_request_text = rg_request_text[1]

    rg_request_box = pygame.Rect(game.width/4,game.height/4, game.width/2,game.height/2)

    rg_request_yes_text = write_text('yes', num_size, return_font=True)
    rg_request_yes_text_size = rg_request_yes_text[0].size('yes')
    rg_request_yes_text = rg_request_yes_text[1]
    rg_request_yesbutton = pygame.Rect(rg_request_box.x+25,rg_request_box.y+rg_request_box.height-65,rg_request_yes_text_size[0]+10,rg_request_yes_text_size[1]+5)

    rg_request_no_text = write_text('no', num_size, return_font=True)
    rg_request_no_text_size = rg_request_no_text[0].size('no')
    rg_request_no_text = rg_request_no_text[1]
    rg_request_nobutton = pygame.Rect(rg_request_box.x+rg_request_box.width-75,rg_request_box.y+rg_request_box.height-65,rg_request_no_text_size[0]+10,rg_request_no_text_size[1]+5)

    topbar_flag_image = pygame.transform.scale(flag_image, (game.width/30,-topbar_y/2))

    counter_start = None
    lost = False
    used_debug_mode = False

    quick_menu_key = cfg['BINDS']['quick_menu']
    quick_menu_key = eval(f'pygame.K_{quick_menu_key}')

    debug_mode_key = cfg['BINDS']['debug_mode']
    debug_mode_key = eval(f'pygame.K_{debug_mode_key}')

    reload_game_key = cfg['BINDS']['reload_game']
    reload_game_key = eval(f'pygame.K_{reload_game_key}')

    game.mainloop()