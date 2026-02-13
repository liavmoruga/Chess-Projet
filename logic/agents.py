import random
import time
import chess

# AGENT INTERFACE

class Agent:
    def __init__(self):
        self.color = None

    def set_color(self, color):
        self.color = color

    def get_move(self, board_obj):
        # return ((start_row, start_col), (end_row, end_col)) or None
        raise NotImplementedError













# BOTS

class RandomBot(Agent):
    def __init__(self, wait_time):
        super().__init__()
        self.wait_time = wait_time

    def get_move(self, board_obj):
        legal_moves = list(board_obj.engine.legal_moves)
        
        if not legal_moves:
            return None 
            
        move = random.choice(legal_moves)
        
        sr = 7 - chess.square_rank(move.from_square)
        sc = chess.square_file(move.from_square)
        er = 7 - chess.square_rank(move.to_square)
        ec = chess.square_file(move.to_square)
        
        time.sleep(self.wait_time)
        return (sr, sc), (er, ec)
    







class MinimaxBot(Agent):
    def __init__(self, depth):
        super().__init__()
        self.depth = depth
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

    def get_move(self, board_obj):
        board = board_obj.engine.copy()
        
        best_move = None
        best_value = -99999 if self.color == chess.WHITE else 99999
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # Loop through root moves
        for move in legal_moves:
            board.push(move)
            value = self.minimax(board, self.depth - 1, not (self.color == chess.WHITE))
            board.pop()
            
            if self.color == chess.WHITE:
                if value > best_value:
                    best_value = value
                    best_move = move
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
        
        if best_move:
            sr = 7 - chess.square_rank(best_move.from_square)
            sc = chess.square_file(best_move.from_square)
            er = 7 - chess.square_rank(best_move.to_square)
            ec = chess.square_file(best_move.to_square)
            return (sr, sc), (er, ec)
            
        return None

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -9999
            else:
                return 9999
        
        if board.is_game_over():
            return 0

        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        return score

    def minimax(self, board, depth, search_max):
        if depth <= 0 or board.is_game_over():
            return self.evaluate_board(board)

        if search_max:
            max_value = -99999
            for move in board.legal_moves:
                board.push(move)
                value = self.minimax(board, depth - 1, False)
                board.pop()
                max_value = max(max_value, value)
            return max_value
        else:
            min_value = 99999
            for move in board.legal_moves:
                board.push(move)
                value = self.minimax(board, depth - 1, True)
                board.pop()
                min_value = min(min_value, value)
            return min_value