# Each piece will inherit from the Piece class
from config.settings.settings import *
from ..userinterface.text import Text
from abc import ABC, abstractmethod
import pygame

class Piece(ABC, pygame.sprite.Sprite):
    def __init__(self, image, side: int, position, board):
        super().__init__()
        self.image = image
        self.side = side    
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.last_position = position
        self.selected = False
        self.board = board
        self.offset = pygame.math.Vector2(0, 0)
        self.is_captured = False
        self.pos = (position[0] // TILESIZE, position[1] // TILESIZE)

    @abstractmethod
    def move(self):
        pass

    def update(self, mousepos):
        self.rect.topleft = (mousepos[0] - 50 - self.offset[0], mousepos[1] - 50 - self.offset[0])

    def snapToGrid(self):
        new_x = round(self.rect.x / TILESIZE) * TILESIZE + TILESIZE // 2 - self.rect.width // 2
        new_y = round(self.rect.y / TILESIZE) * TILESIZE + TILESIZE // 2 - self.rect.height // 2
        self.rect.x = max(0, min(new_x, BOARDSIZE - TILESIZE))
        self.rect.y = max(0, min(new_y, BOARDSIZE - TILESIZE))

    def checkCollision(self, mousepos):
        return self.rect.collidepoint(mousepos)

    def draw(self, screen, offset: tuple | None = None):
        if offset is None:
            offset = (0, 0)
        if self.selected:
            if self.side == 0:
                pygame.draw.rect(screen, COLOR['BLACK'], self.rect.inflate(10, 10), 3)
            else:
                pygame.draw.rect(screen, COLOR['WHITE'], self.rect.inflate(10, 10), 3)
        screen.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))

    def reset_to_last_position(self):
        """Reset the piece to the last position if the move is invalid."""
        self.rect.topleft = self.last_position
        self.pos = (self.last_position[0] // TILESIZE, self.last_position[1] // TILESIZE)

    @abstractmethod
    def get_possible_moves(self, chessboard=None):
        """Return a list of possible moves for the piece."""
        pass

    def get_position(self):
        """Get the current position of the piece on the board (0-7, 0-7)"""
        return (self.rect.x // TILESIZE, self.rect.y // TILESIZE)

    def is_valid_position(self, x, y):
        """Check if the position (x,y) is on the board"""
        return 0 <= x < 8 and 0 <= y < 8

    def is_enemy_or_empty(self, x, y):
        """Check if the position (x,y) is empty or has an enemy piece"""
        piece = self.board.map[y][x]
        if piece is None:
            return True
        return piece.side != self.side

    def move(self, x, y):
        old_x, old_y = self.get_position()
        self.board.map[old_y][old_x] = None
        target_piece = self.board.map[y][x]
        if target_piece is not None:
            target_piece.is_captured = True            
        self.board.map[y][x] = self
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.pos = (x, y)
        self.last_position = (self.rect.x, self.rect.y)