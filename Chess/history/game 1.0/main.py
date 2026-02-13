import pygame
import sys
import settings
from assets.assets import AssetManager
from logic.board import Board
from logic.bot import Bot

# MAIN GAME

class ChessGame:
    def __init__(self, mode='local'):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Chess Project - Liav Moruga")
        self.clock = pygame.time.Clock()
        
        self.assets = AssetManager()
        self.assets.load_content()
        
        self.board = Board()
        self.bot = Bot()
        self.mode = mode
        
        # state
        self.selected_square = None
        self.valid_moves = []
        self.is_dragging = False
        self.drag_piece_data = None
        self.clicked_selected = False
        self.flip_view = False
        
        # layout
        self.sq_size = 0
        self.board_x = 0
        self.board_y = 0
        self.coord_font = None
        
        self._recalculate_layout(settings.WIDTH, settings.HEIGHT)

    def _recalculate_layout(self, w, h):
        min_dim = min(w, h)
        self.sq_size = min_dim // 8
        self.board_x = (w - (self.sq_size * 8)) // 2
        self.board_y = (h - (self.sq_size * 8)) // 2
        
        self.coord_font = pygame.font.SysFont('Arial', int(self.sq_size * 0.18), bold=True)
        
        # resize images
        self.assets.rescale_images(self.sq_size)

    def _deselect(self):
        self.selected_square = None
        self.valid_moves = []
        self.is_dragging = False
        self.drag_piece_data = None
        self.clicked_selected = False

    def _get_board_pos(self, mouse_pos):
        mx, my = mouse_pos[0] - self.board_x, mouse_pos[1] - self.board_y
        if self.sq_size > 0:
            row = my // self.sq_size
            col = mx // self.sq_size
            if self.flip_view:
                row = 7 - row
                col = 7 - col
            if 0 <= row < 8 and 0 <= col < 8:
                return (row, col)
        return None

    def _handle_click(self, pos):
        # don't allow click if game over
        if self.board.is_game_over(): return

        coords = self._get_board_pos(pos)
        if not coords:
            self._deselect()
            return

        # click valid move
        if coords in self.valid_moves:
            self._execute_move(self.selected_square, coords)
            return

        # click piece
        piece = self.board.get_piece_at(*coords)
        if self.board.is_turn(piece):
            if self.selected_square == coords:
                self.clicked_selected = True
            else:
                self.clicked_selected = False
            
            self.selected_square = coords
            self.valid_moves = self.board.get_valid_moves(coords)
            self.is_dragging = True
            self.drag_piece_data = {'symbol': piece, 'pos': coords}
        else:
            self._deselect()

    def _handle_release(self):
        if self.is_dragging:
            coords = self._get_board_pos(pygame.mouse.get_pos())
            if coords and coords in self.valid_moves and coords != self.selected_square:
                self._execute_move(self.selected_square, coords)
            
            self.is_dragging = False
            self.drag_piece_data = None
            if self.clicked_selected: self._deselect()

    def _execute_move(self, start, end):
        is_capture = self.board.move_piece(start, end)
        self.assets.play_sound('capture' if is_capture else 'move')
        self._deselect()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self._recalculate_layout(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f: self.flip_view = not self.flip_view
                
                # human input
                if not (self.mode == 'bot' and not self.board.engine.turn):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self._handle_click(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self._handle_release()

            # bot turn
            if self.mode == 'bot' and not self.board.engine.turn and not self.board.is_game_over():
                pygame.time.wait(200)
                move = self.bot.get_random_move(self.board)
                if move:
                    self._execute_move(move[0], move[1])

            # draw
            self.screen.fill(settings.BACKGROUND)
            self._draw_board()
            self._draw_hints()
            self._draw_pieces()
            
            pygame.display.flip()
            self.clock.tick(settings.FPS)

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                dr = 7 - r if self.flip_view else r
                dc = 7 - c if self.flip_view else c
                x = self.board_x + dc * self.sq_size
                y = self.board_y + dr * self.sq_size
                
                # colors
                color = settings.LIGHT_BROWN if (r+c)%2==0 else settings.DARK_BROWN
                
                # last move
                if self.board.last_move:
                    if (r,c) == self.board.last_move[0]: color = settings.SOURCE_COLOR
                    elif (r,c) == self.board.last_move[1]: color = settings.DEST_COLOR
                
                # selection
                if self.selected_square == (r,c): color = settings.SELECTED_COLOR
                
                # check highlight (red under king)
                if self.board.is_in_check():
                    king_pos = self.board.get_king_pos()
                    if king_pos == (r, c):
                        color = settings.CHECK_COLOR

                pygame.draw.rect(self.screen, color, (x, y, self.sq_size, self.sq_size))
                
                # coords
                txt_color = settings.DARK_BROWN if (r+c)%2==0 else settings.LIGHT_BROWN
                pad = int(self.sq_size * 0.03)
                
                if dc == 7: 
                    lbl = self.coord_font.render(str(8-r), True, txt_color)
                    self.screen.blit(lbl, (x + self.sq_size - lbl.get_width() - pad, y + pad))
                if dr == 7: 
                    lbl = self.coord_font.render(chr(ord('a')+c), True, txt_color)
                    self.screen.blit(lbl, (x + pad, y + self.sq_size - lbl.get_height() - pad))

    def _draw_hints(self):
        for (r, c) in self.valid_moves:
            dr = 7 - r if self.flip_view else r
            dc = 7 - c if self.flip_view else c
            x = self.board_x + dc * self.sq_size
            y = self.board_y + dr * self.sq_size
            
            target = self.board.get_piece_at(r, c)
            s = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            
            if not target:
                rad = int(self.sq_size * 0.125)
                pygame.draw.circle(s, settings.HINT_COLOR, (self.sq_size//2, self.sq_size//2), rad)
            else:
                tl = int(self.sq_size * 0.2)
                w, h = self.sq_size, self.sq_size
                pygame.draw.polygon(s, settings.HINT_COLOR, [(0,0), (tl,0), (0,tl)])
                pygame.draw.polygon(s, settings.HINT_COLOR, [(w,0), (w-tl,0), (w,tl)])
                pygame.draw.polygon(s, settings.HINT_COLOR, [(0,h), (0,h-tl), (tl,h)])
                pygame.draw.polygon(s, settings.HINT_COLOR, [(w,h), (w-tl,h), (w,h-tl)])
            self.screen.blit(s, (x, y))

    def _draw_pieces(self):
        mx, my = pygame.mouse.get_pos()
        is_checkmate = self.board.is_checkmate()
        
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece_at(r, c)
                if piece:
                    if self.is_dragging and self.drag_piece_data['pos'] == (r, c): continue
                    
                    dr = 7 - r if self.flip_view else r
                    dc = 7 - c if self.flip_view else c
                    x = self.board_x + dc * self.sq_size
                    y = self.board_y + dr * self.sq_size
                    
                    img = self.assets.get_image(piece)
                    
                    # rotate king if checkmate
                    # (logic: if it is checkmate, and this piece is the king of the current turn)
                    if is_checkmate and piece.lower() == 'k' and self.board.is_turn(piece):
                        # rotate 90 degrees
                        img = pygame.transform.rotate(img, 90)
                        # recenter because rotation can change rect size slightly
                        new_rect = img.get_rect(center=(x + self.sq_size//2, y + self.sq_size//2))
                        self.screen.blit(img, new_rect)
                    else:
                        if img: self.screen.blit(img, (x, y))

        if self.is_dragging and self.drag_piece_data:
            piece = self.drag_piece_data['symbol']
            img = self.assets.get_image(piece)
            if img:
                rect = img.get_rect(center=(mx, my))
                self.screen.blit(img, rect)

if __name__ == "__main__":
    game = ChessGame(mode='local') # or 'bot'
    game.run()