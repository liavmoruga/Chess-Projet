import chess

# BOARD LOGIC

class Board:
    def __init__(self):
        self.engine = chess.Board()
        self.last_move = None

    def get_piece_at(self, row, col):
        # convert (row, col) to chess square index
        # row 0 is rank 8, row 7 is rank 1
        square = chess.square(col, 7 - row)
        piece = self.engine.piece_at(square)
        return piece.symbol() if piece else None

    def get_valid_moves(self, start_pos):
        r, c = start_pos
        start_sq = chess.square(c, 7 - r)
        
        moves = []
        # get all legal moves for this square
        for move in self.engine.legal_moves:
            if move.from_square == start_sq:
                # convert target square back to (row, col)
                tr = 7 - chess.square_rank(move.to_square)
                tc = chess.square_file(move.to_square)
                moves.append((tr, tc))
        return moves

    def move_piece(self, start, end):
        sr, sc = start
        er, ec = end
        
        start_sq = chess.square(sc, 7 - sr)
        end_sq = chess.square(ec, 7 - er)
        
        # find the matching move object (handling promotion automatically to queen for simplicity)
        move_to_make = None
        for move in self.engine.legal_moves:
            if move.from_square == start_sq and move.to_square == end_sq:
                move_to_make = move
                break
        
        if move_to_make:
            is_capture = self.engine.is_capture(move_to_make)
            self.engine.push(move_to_make)
            self.last_move = (start, end)
            return is_capture
            
        return False

    def is_turn(self, piece_symbol):
        if not piece_symbol: return False
        # engine.turn is True for white, False for black
        is_white_piece = piece_symbol.isupper()
        return is_white_piece == self.engine.turn

    def is_game_over(self):
        return self.engine.is_game_over()

    def is_in_check(self):
        return self.engine.is_check()

    def is_checkmate(self):
        return self.engine.is_checkmate()

    def get_king_pos(self):
        # find king of current turn
        king_sq = self.engine.king(self.engine.turn)
        if king_sq is not None:
            return (7 - chess.square_rank(king_sq), chess.square_file(king_sq))
        return None