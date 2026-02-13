import pygame
import sys
import os

# DEFAULTS

WIDTH, HEIGHT = 640, 640
FPS = 60

# will be updated dynamically on resize
SQ_SIZE = 0
BOARD_X = 0
BOARD_Y = 0

HINT_DOT_RADIUS = 0
HINT_TRIANGLE_LEN = 0
COORD_PADDING = 0

COORD_FONT = None
PLACEHOLDER_FONT = None

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (30, 30, 30) 
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)

SELECTED_COLOR = (100, 109, 64)
HINT_COLOR = (100, 109, 64, 128)
SOURCE_COLOR = (206, 210, 107)
DEST_COLOR = (170, 162, 58)




# ASSETS

ORIGINAL_IMAGES = {}
SCALED_IMAGES = {}
SOUNDS = {}





def load_assets():
    global ORIGINAL_IMAGES
    
    # sounds
    files = {'move': 'move.ogg', 'capture': 'capture.ogg'}
    for name, filename in files.items():
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(curr_dir, "sounds", filename)
        if os.path.exists(path):
            SOUNDS[name] = pygame.mixer.Sound(path)

    # original images
    pieces = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename in pieces:
        key = filename[1].upper() if filename.startswith('w') else filename[1]
        
        path = os.path.join(curr_dir, "images", f"{filename}.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            ORIGINAL_IMAGES[key] = img
        else:
            ORIGINAL_IMAGES[key] = None

def recalculate_layout(w, h):
    global SQ_SIZE, BOARD_X, BOARD_Y
    global HINT_DOT_RADIUS, HINT_TRIANGLE_LEN, COORD_PADDING
    global COORD_FONT, PLACEHOLDER_FONT, SCALED_IMAGES
    
    # calculate dimensions
    min_dim = min(w, h)
    SQ_SIZE = min_dim // 8
    BOARD_X = (w - (SQ_SIZE * 8)) // 2
    BOARD_Y = (h - (SQ_SIZE * 8)) // 2

    # update relative sizes
    HINT_DOT_RADIUS = int(SQ_SIZE * 0.125)
    HINT_TRIANGLE_LEN = int(SQ_SIZE * 0.2)
    COORD_PADDING = int(SQ_SIZE * 0.03)
    coord_font_size = int(SQ_SIZE * 0.18)
    placeholder_font_size = int(SQ_SIZE * 0.4)

    # update fonts
    COORD_FONT = pygame.font.SysFont('Arial', coord_font_size, bold=True)
    PLACEHOLDER_FONT = pygame.font.SysFont("Arial", placeholder_font_size, bold=True)

    # rescale images
    SCALED_IMAGES.clear()
    for key, original_img in ORIGINAL_IMAGES.items():
        if original_img:
            SCALED_IMAGES[key] = pygame.transform.smoothscale(original_img, (SQ_SIZE, SQ_SIZE))
        else:
            #make a placeholder if image is not found
            image = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            text_color = BLACK if key.islower() else WHITE
            text = PLACEHOLDER_FONT.render(key, True, text_color)
            text_rect = text.get_rect(center=(SQ_SIZE//2, SQ_SIZE//2))
            image.blit(text, text_rect)
            SCALED_IMAGES[key] = image

def play_sound(is_capture):
    key = 'capture' if is_capture else 'move'
    if key in SOUNDS:
        SOUNDS[key].play()




# LOGIC

def parse_fen(fen):
    board = [['' for _ in range(8)] for _ in range(8)]
    row, col = 0, 0
    for char in fen.split(' ')[0]:
        if char == '/':
            row += 1
            col = 0
        elif char.isdigit():
            col += int(char)
        else:
            board[row][col] = char
            col += 1
    return board

def get_valid_moves(board, pos):
    r, c = pos
    moves = []
    directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(-1,1),(1,-1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            moves.append((nr, nc))
    return moves

def move_piece(board, start, end):
    sr, sc = start
    er, ec = end
    board[er][ec] = board[sr][sc]
    board[sr][sc] = ''





# DRAWING

def draw_board(screen, selected_square, last_move, flip_view=False):
    for row in range(8):
        for col in range(8):
            draw_r = 7 - row if flip_view else row
            draw_c = 7 - col if flip_view else col

            x = BOARD_X + draw_c * SQ_SIZE
            y = BOARD_Y + draw_r * SQ_SIZE

            is_light = (row + col) % 2 == 0
            base_color = LIGHT_BROWN if is_light else DARK_BROWN
            
            color = base_color
            if last_move:
                if (row, col) == last_move[0]: color = SOURCE_COLOR
                elif (row, col) == last_move[1]: color = DEST_COLOR
            if selected_square == (row, col):
                color = SELECTED_COLOR
            
            pygame.draw.rect(screen, color, (x, y, SQ_SIZE, SQ_SIZE))

            text_color = DARK_BROWN if is_light else LIGHT_BROWN
            
            if draw_c == 7:
                text = str(8 - row)
                label = COORD_FONT.render(text, True, text_color)
                screen.blit(label, (x + SQ_SIZE - label.get_width() - COORD_PADDING, y + COORD_PADDING))

            if draw_r == 7:
                text = chr(ord('a') + col)
                label = COORD_FONT.render(text, True, text_color)
                screen.blit(label, (x + COORD_PADDING, y + SQ_SIZE - label.get_height() - COORD_PADDING))

def draw_move_hints(screen, board, valid_moves, flip_view):
    for (row, col) in valid_moves:
        if not (0 <= row < 8 and 0 <= col < 8): continue

        draw_r = 7 - row if flip_view else row
        draw_c = 7 - col if flip_view else col
        
        x = BOARD_X + draw_c * SQ_SIZE
        y = BOARD_Y + draw_r * SQ_SIZE
        
        target_piece = board[row][col]

        if target_piece == '':
            center = (x + SQ_SIZE // 2, y + SQ_SIZE // 2)
            pygame.draw.circle(screen, HINT_COLOR, center, HINT_DOT_RADIUS)
        else:
            tl = HINT_TRIANGLE_LEN
            pygame.draw.polygon(screen, HINT_COLOR, [(x, y), (x + tl, y), (x, y + tl)])
            pygame.draw.polygon(screen, HINT_COLOR, [(x + SQ_SIZE, y), (x + SQ_SIZE - tl, y), (x + SQ_SIZE, y + tl)])
            pygame.draw.polygon(screen, HINT_COLOR, [(x, y + SQ_SIZE), (x, y + SQ_SIZE - tl), (x + tl, y + SQ_SIZE)])
            pygame.draw.polygon(screen, HINT_COLOR, [(x + SQ_SIZE, y + SQ_SIZE), (x + SQ_SIZE - tl, y + SQ_SIZE), (x + SQ_SIZE, y + SQ_SIZE - tl)])

def draw_pieces(screen, board, dragging_piece, dragging_pos, flip_view):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                if dragging_piece and dragging_piece['pos'] == (row, col):
                    continue

                draw_r = 7 - row if flip_view else row
                draw_c = 7 - col if flip_view else col
                
                x = BOARD_X + draw_c * SQ_SIZE
                y = BOARD_Y + draw_r * SQ_SIZE
                
                screen.blit(SCALED_IMAGES[piece], (x, y))

    if dragging_piece:
        m_x, m_y = dragging_pos
        symbol = dragging_piece['symbol']
        rect = SCALED_IMAGES[symbol].get_rect(center=(m_x, m_y))
        screen.blit(SCALED_IMAGES[symbol], rect)





# MAIN LOOP

def mainloop():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Chess Project - Liav Moruga")
    
    load_assets()
    recalculate_layout(WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    running = True

    board = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    last_move = None         
    selected_square = None   
    valid_moves = []         
    is_dragging = False
    clicked_selected_piece = False 
    flip_view = False

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        mx, my = mouse_pos[0] - BOARD_X, mouse_pos[1] - BOARD_Y
        
        if SQ_SIZE > 0:
            row = my // SQ_SIZE
            col = mx // SQ_SIZE
        else:
            row, col = -1, -1
        
        if flip_view:
            row = 7 - row
            col = 7 - col
        
        is_in_board = (0 <= row < 8) and (0 <= col < 8)
        current_hover = (row, col) if is_in_board else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                recalculate_layout(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    flip_view = not flip_view

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # if pressing outside the board deselect
                if not current_hover:
                    selected_square = None
                    valid_moves = []
                    is_dragging = False
                    clicked_selected_piece = False
                    continue
                
                # if clicking on a valid move
                if current_hover in valid_moves:
                    is_capture = board[current_hover[0]][current_hover[1]] != ''
                    play_sound(is_capture)
                    move_piece(board, selected_square, current_hover)
                    last_move = (selected_square, current_hover)
                    selected_square = None
                    valid_moves = []
                    is_dragging = False
                    clicked_selected_piece = False

                #if clicking a piece
                elif board[row][col] != '':
                    if selected_square == current_hover:
                        clicked_selected_piece = True
                    else:
                        clicked_selected_piece = False

                    selected_square = current_hover
                    is_dragging = True
                    valid_moves = get_valid_moves(board, selected_square)
                
                else:
                    selected_square = None
                    valid_moves = []
                    is_dragging = False
                    clicked_selected_piece = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if is_dragging:
                    #if dragged to a valid move
                    if current_hover and current_hover != selected_square:
                        if current_hover in valid_moves:
                            is_capture = board[current_hover[0]][current_hover[1]] != ''
                            play_sound(is_capture)
                            move_piece(board, selected_square, current_hover)
                            last_move = (selected_square, current_hover)

                        selected_square = None
                        valid_moves = []
                    
                    #if click on the selected piece deselect
                    else:
                        if clicked_selected_piece:
                            selected_square = None
                            valid_moves = []
                    
                    is_dragging = False

        drag_data = None
        if is_dragging and selected_square:
            piece = board[selected_square[0]][selected_square[1]]
            drag_data = {'symbol': piece, 'pos': selected_square}

        screen.fill(BACKGROUND)
        
        draw_board(screen, selected_square, last_move, flip_view)
        draw_move_hints(screen, board, valid_moves, flip_view)
        draw_pieces(screen, board, drag_data, mouse_pos, flip_view)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    mainloop()