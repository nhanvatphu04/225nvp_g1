import pygame
import os
import numpy
from utils.resource_manager import ResourceManager
import sys

# Khởi tạo ResourceManager (sẽ tự động khởi tạo pygame)
resource_manager = ResourceManager()

SCREENWIDTH = 1200
SCREENHEIGHT = 900
TILESIZE = 100
BOARDSIZE = TILESIZE * 8

COLOR = {
    'BLACK'  : (0  , 0  ,   0),
    'WHITE'  : (255, 255, 255),
    'GREEN'  : (0  , 255,   0),
    'RED'    : (255,   0,   0),
    'LIME'   : (0  , 255,   0),
    'BLUE'   : (0  ,   0, 255),
    'YELLOW' : (255, 255,   0),
    'GREY'   : (128, 128, 128)
}

# Đặt FONTS sau khi pygame đã được khởi tạo
FONTS = {
    'TITLE': resource_manager.load_font('04B_30__.ttf', 74),
    'MENU': resource_manager.load_font('04B_30__.ttf', 36),
    'GAME': resource_manager.load_font('04B_30__.ttf', 24),
    'DEFAULT': resource_manager.load_font(None, 20)
}

FONT_SIZES = {
    'LARGE': 74,
    'MEDIUM': 36,
    'SMALL': 24,
    'TINY': 16
}

FPS = 60
OFFSET = 0

# Board dimensions
BOARD_WIDTH = 800
BOARD_HEIGHT = 800
SQUARE_SIZE = 100
BOARD_OFFSET_X = 0
BOARD_OFFSET_Y = 0

# Load game resources
ICON = resource_manager.load_image('icon.png')
BACKGROUND = resource_manager.get_resource_path('assets/background/mikudance.gif')
BGMUSIC = resource_manager.get_resource_path('assets/bgmusic/avangard.mp3')

# Load piece images
bishop = [
    resource_manager.load_image('white_bishop.png'),
    resource_manager.load_image('black_bishop.png')
]

king = [
    resource_manager.load_image('white_king.png'),
    resource_manager.load_image('black_king.png')
]

knight = [
    resource_manager.load_image('white_knight.png'),
    resource_manager.load_image('black_knight.png')
]

pawn = [
    resource_manager.load_image('white_pawn.png'),
    resource_manager.load_image('black_pawn.png')
]

queen = [
    resource_manager.load_image('white_queen.png'),
    resource_manager.load_image('black_queen.png')
]

rook = [
    resource_manager.load_image('white_rook.png'),
    resource_manager.load_image('black_rook.png')
]

# Load chessboard images
chessboard = [
    resource_manager.load_image('chessboard_grey.png'),
    resource_manager.load_image('chessboard_red.png')
]

# Kiểm tra xem images đã load thành công chưa
if None in chessboard:
    sys.exit(1)

# Board positions
boardset = {}
for row in range(8):
    for col in range(8):
        position_key = f"{chr(97 + col)}{8 - row}"
        boardset[position_key] = numpy.array([col * 100, row * 100])

def scale2x(img: pygame.Surface):
    if img is None:
        return None
    size = img.get_size()
    scale_img = pygame.transform.scale(img, (size[0] * 2, size[1] * 2))
    return scale_img
