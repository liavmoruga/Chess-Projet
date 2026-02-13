import random
import time
import chess

# AGENT INTERFACE

class Agent:
    def __init__(self):
        self.color = None  # will be chess.WHITE or chess.BLACK

    def set_color(self, color):
        # sets the side this agent is playing
        self.color = color

    def get_move(self, board_obj):
        # should return ((start_row, start_col), (end_row, end_col)) or None
        raise NotImplementedError

# CONCRETE BOTS

class RandomBot(Agent):
    def get_move(self, board_obj):
        # simulate thinking time so we can see threading works
        time.sleep(0.5)

        # board_obj is our wrapper, board_obj.engine is the chess library object
        legal_moves = list(board_obj.engine.legal_moves)
        
        if not legal_moves:
            return None 
            
        move = random.choice(legal_moves)
        
        # convert chess.Move back to UI coordinates (start, end)
        sr = 7 - chess.square_rank(move.from_square)
        sc = chess.square_file(move.from_square)
        er = 7 - chess.square_rank(move.to_square)
        ec = chess.square_file(move.to_square)
        
        return (sr, sc), (er, ec)