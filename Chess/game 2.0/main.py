import pygame
import sys
import random
import threading
import chess
import settings
from assets.assets import AssetManager
from logic.board import Board
from logic.agents import RandomBot

# MAIN GAME

class ChessGame:
    def __init__(self, white_agent=None, black_agent=None):
        # white_agent/black_agent: None for human, Agent object for bot/online
        
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Chess Project - Liav Moruga")
        self.clock = pygame.time.Clock()
        
        self.assets = AssetManager()
        self.assets.load_content()
        
        self.board = Board()
        
        # agents
        self.white_agent = white_agent
        self.black_agent = black_agent
        
        # set agent colors
        if self.white_agent: self.white_agent.set_color(chess.WHITE)
        if self.black_agent: self.black_agent.set_color(chess.BLACK)
        
        # view settings
        self.flip_view = False
        # auto-flip if human plays black (white is bot, black is human)
        if self.white_agent is not None and self.black_agent is None:
            self.flip_view = True
        
        # state
        self.selected_square = None
        self.valid_moves = []
        self.is_dragging = False
        self.drag_piece_data = None
        self.clicked_selected = False
        
        # threading state
        self.agent_thinking = False
        self.agent_move_result = None
        self.agent_thread = None
        
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
        # checks
        if self.board.is_game_over(): return

        coords = self._get_board_pos(pos)
        if not coords:
            self._deselect()
            return

        # click on valid move
        if coords in self.valid_moves:
            self._execute_move(self.selected_square, coords)
            return

        # click on piece
        piece = self.board.get_piece_at(*coords)
        if self.board.is_piece_turn(piece):
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

    def _run_agent_move(self, agent):
        # runs in separate thread
        try:
            move = agent.get_move(self.board)
            self.agent_move_result = move
        except Exception as e:
            print(f"agent error: {e}")
            self.agent_move_result = None

    def run(self):
        while True:
            # check turn
            is_white = self.board.is_turn
            current_agent = self.white_agent if is_white else self.black_agent
            
            # event loop
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
                # only allow if it's human turn (agent is None) and not waiting for thread
                if current_agent is None and not self.agent_thinking and not self.board.is_game_over():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self._handle_click(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self._handle_release()

            # agent logic
            if current_agent is not None and not self.board.is_game_over():
                if not self.agent_thinking:
                    # start thinking
                    self.agent_thinking = True
                    self.agent_thread = threading.Thread(target=self._run_agent_move, args=(current_agent,))
                    self.agent_thread.start()
                
                # check if done
                if not self.agent_thread.is_alive():
                    if self.agent_move_result:
                        start, end = self.agent_move_result
                        self._execute_move(start, end)
                    self.agent_thinking = False
                    self.agent_move_result = None

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
                
                # tile colors
                color = settings.LIGHT_BROWN if (r+c)%2==0 else settings.DARK_BROWN
                
                # last move highlight
                if self.board.last_move:
                    if (r,c) == self.board.last_move[0]: color = settings.SOURCE_COLOR
                    elif (r,c) == self.board.last_move[1]: color = settings.DEST_COLOR
                
                # selection highlight
                if self.selected_square == (r,c): color = settings.SELECTED_COLOR
                
                # check highlight
                if self.board.is_in_check():
                    king_pos = self.board.get_king_pos()
                    if king_pos == (r, c):
                        color = settings.CHECK_COLOR

                pygame.draw.rect(self.screen, color, (x, y, self.sq_size, self.sq_size))
                
                # coordinates
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
                    if is_checkmate and piece.lower() == 'k' and self.board.is_piece_turn(piece):
                        img = pygame.transform.rotate(img, 90)
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


def run_game(mode='pvp', opponent_cls=None, side='r'):
    # helper to setup game modes
    # mode: 'pvp', 'pve' (player vs engine), 'eve' (engine vs engine)
    # side: 'w', 'b', 'r' (random) - only applies to pve
    
    w_agent = None
    b_agent = None
    
    if mode == 'pvp':
        pass
    
    elif mode == 'eve':
        # both sides are bots
        w_agent = opponent_cls()
        b_agent = opponent_cls()
        
    elif mode == 'pve':
        # decide side
        if side == 'r':
            side = random.choice(['w', 'b'])
            
        if side == 'w':
            # player is white, bot is black
            w_agent = None
            b_agent = opponent_cls()
        else:
            # player is black, bot is white
            w_agent = opponent_cls()
            b_agent = None
            
    game = ChessGame(white_agent=w_agent, black_agent=b_agent)
    game.run()

if __name__ == "__main__":
    # CONFIGURATION
    
    # example 1: play against random bot as white
    # run_game(mode='pve', opponent_cls=RandomBot, side='w')
    
    # example 2: watch two bots play
    run_game(mode='eve', opponent_cls=RandomBot)

    # example 3: local multiplayer
    # run_game(mode='pvp')