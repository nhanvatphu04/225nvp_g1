from config.settings.settings import *
import pygame

chessboard[0] = scale2x(chessboard[0])
chessboard[1] = scale2x(chessboard[1])

class ChessBoard():
    def __init__(self):
        self.size = TILESIZE
        self.chessboard = [chessboard[0], chessboard[1]]
        self.surface = pygame.Surface((self.size * 8, self.size * 8))
        self.map = [[None for _ in range(8)] for _ in range(8)]
        self.drawSurface()

    def place_piece(self, piece):
        """Place piece on the chessboard"""
        x, y = piece.rect.topleft
        grid_x = x // TILESIZE
        grid_y = y // TILESIZE
        self.map[grid_y][grid_x] = piece

    def is_occupied(self, grid_x, grid_y):
        """Check if the position on the chessboard is occupied"""
        return self.map[grid_y][grid_x] is not None

    def move_piece(self, piece, new_x, new_y):
        """Move piece and update position on the map"""
        old_x, old_y = piece.rect.topleft
        grid_old_x, grid_old_y = old_x // TILESIZE, old_y // TILESIZE
        grid_new_x, grid_new_y = new_x // TILESIZE, new_y // TILESIZE
        if not self.is_occupied(grid_new_x, grid_new_y):
            piece.rect.topleft = (new_x, new_y)
            self.map[grid_new_y][grid_new_x] = piece
            self.map[grid_old_y][grid_old_x] = None
        else:
            piece.rect.topleft = (old_x, old_y)

    def drawSurface(self):
        for row in range(8):
            for col in range(8):
                x = col * self.size
                y = row * self.size
                if (row + col) % 2 == 0:
                    self.surface.blit(self.chessboard[0], (x, y))
                else:
                    self.surface.blit(self.chessboard[1], (x, y))
        for x in range(0, BOARDSIZE + 10, TILESIZE):
            pygame.draw.line(self.surface, (200, 200, 200), (x, 0), (x, 800), 5)
        for y in range(0, BOARDSIZE + 10, TILESIZE):
            pygame.draw.line(self.surface, (200, 200, 200), (0, y), (800, y), 5)
    
    def draw(self, screen, offset: tuple | None = None):
        if offset is None:
            offset = (0, 0) 
        screen.blit(self.surface, offset)

    def draw_map_info(self, screen):
        """Method to check map   
        Only used when checking piece position   
        Setting screen 1600x900"""
        font = pygame.font.SysFont(None, 24)
        x_offset = 800  # Coordinate x to draw information table next to the chessboard
        y_offset = 0
        for row_index, row in enumerate(self.map):
            for col_index, cell in enumerate(row):
                label_text = type(cell).__name__ if cell is not None else "None"
                label = font.render(label_text, True, COLOR['BLACK'])
                label_x = x_offset + col_index * 100 + 25
                label_y = y_offset + row_index * 100 + 50
                screen.blit(label, (label_x, label_y))
