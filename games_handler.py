import os
import json

class Game: # talvez fazer uma forma de mostrar como foi o jogo inteiro (pode usar uma array q adiciona cada bloco pressionado que foi negoçado e q foi bomba q ativou e pa ou sla)
    def __init__(self, filename:str ):
        self.filename = filename
        
        if not os.path.exists(self.filename):
            with open(self.filename, 'w+') as f:
                f.write('{}')
        else:
            index = 1
            path = self.filename.split(os.sep)[:-1]
            temp = ''
            for d in path:
                temp += d + os.sep
            path = temp
            if len(path) == 0:
                path = '.'
            dir = os.listdir(path)
            default_title = self.filename
            fn = os.path.basename(self.filename)
            for title in dir:
                if title == fn:
                    fn = default_title.replace('.json','')+str(index)+'.json'
                    index += 1
            self.filename = fn
            
            with open(self.filename, 'w+') as f:
                f.write('{}')
        
        self.content = json.load(open(self.filename,'r'))
            
    def add_game(self, time: float, default_lives: int, won_game: bool, bombs: int, grid_w_amount: float, grid_h_amount: float, window_width: int, window_height: int, actions: list, squares: list): # se lembrar de botar mais informação do jogo
        self.content = {
            'time':time,
            'default_lives':default_lives,
            'won':won_game,
            'bombs':bombs,
            'grid_w_amount':grid_w_amount,
            'grid_h_amount':grid_h_amount,
            'width':window_width,
            'height':window_height,
            'actions':actions,
            'squares':squares
        }

        json.dump(self.content, open(self.filename, 'w+'))