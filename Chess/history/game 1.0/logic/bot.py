import random
import chess

# BOT LOGIC

class Bot:
    def get_random_move(self, board_obj):
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