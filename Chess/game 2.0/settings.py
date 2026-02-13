import os

# SETTINGS

# dimensions
WIDTH = 640
HEIGHT = 640
FPS = 60

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")

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
CHECK_COLOR = (255, 0, 0)