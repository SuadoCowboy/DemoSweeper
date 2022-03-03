import os
import json

class Games: # talvez fazer uma forma de mostrar como foi o jogo inteiro (pode usar uma array q adiciona cada bloco pressionado que foi negoçado e q foi bomba q ativou e pa ou sla)
    def __init__(self, filename:str ):
        self.filename = filename
        
        if not os.path.exists(self.filename):
            with open(self.filename, 'w+') as f:
                f.write('{}')
        
        self.content = json.load(open(self.filename,'r'))
            
    def add_game(self, game_title: str, time: float, default_lives: int, won_game: bool, bombs: int, grid_w_amount: float, grid_h_amount: float, window_width: int, window_height: int, actions: list, squares: list): # se lembrar de botar mais informação do jogo
        default_title = game_title
        index = 1
        for title in self.content:
            if title == game_title:
                game_title = default_title+str(index)
                index += 1
        
        self.content[game_title] = {
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