from config.settings.settings import *
from .piece import Piece
from .queen import Queen
from .rook import Rook
from .bishop import Bishop
from .knight import Knight
from src.userinterface import Text
import pygame

pawn[0] = scale2x(pawn[0])
pawn[1] = scale2x(pawn[1])

class Pawn(Piece):
    def __init__(self, side, position, board):
        """
        side 0 = White   
        side 1 = Black
        """
        image = pawn[0] if side == 0 else pawn[1]
        super().__init__(image, side, position, board)
        self.first_move = True
        self.just_moved_two = False
        self.can_be_captured_en_passant = False
        self.promotion_options = {
            'Q': Queen,
            'R': Rook,
            'B': Bishop,
            'N': Knight
        }
        self.is_promoting = False

    def get_possible_moves(self, chessboard=None):
        moves = []
        x, y = self.get_position()
        direction = -1 if self.side == 0 else 1
        next_y = y + direction
        if self.is_valid_position(x, next_y) and self.board.map[next_y][x] is None:
            moves.append((x, next_y))
            if self.first_move:
                double_y = y + (direction * 2)
                if (self.is_valid_position(x, double_y) and 
                    self.board.map[double_y][x] is None):
                    moves.append((x, double_y))
        for dx in [-1, 1]:
            new_x = x + dx
            new_y = y + direction
            if self.is_valid_position(new_x, new_y):
                piece = self.board.map[new_y][new_x]
                if piece is not None and piece.side != self.side:
                    moves.append((new_x, new_y))
                elif piece is None:
                    adjacent_piece = self.board.map[y][new_x]
                    if (isinstance(adjacent_piece, Pawn) and 
                        adjacent_piece.side != self.side and 
                        adjacent_piece.can_be_captured_en_passant and
                        ((self.side == 0 and y == 3) or (self.side == 1 and y == 4))):
                        moves.append((new_x, new_y))
        return moves

    def move(self, x, y):
        """Move the pawn to a new position"""
        old_x, old_y = self.get_position()
        self.just_moved_two = abs(y - old_y) == 2
        self.can_be_captured_en_passant = self.just_moved_two
        if abs(x - old_x) == 1 and self.board.map[y][x] is None:
            captured_pawn = self.board.map[old_y][x]
            if isinstance(captured_pawn, Pawn):
                self.board.map[old_y][x] = None
        self.board.map[old_y][old_x] = None
        self.board.map[y][x] = self
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.pos = (x, y)
        self.last_position = (self.rect.x, self.rect.y)
        self.first_move = False
        if self.can_promote():
            self.is_promoting = True
            self.draw_promotion_menu()
            return True
        return False

    def can_promote(self):
        """Check if the pawn can promote"""
        x, y = self.get_position()        
        if self.side == 0 and y == 0:
            return True
        if self.side == 1 and y == 7:
            return True
        return False

    def promote(self, key):
        """Process promotion with the selected key"""
        if not self.is_promoting:
            return None
        x, y = self.get_position()
        choice = chr(key).upper()
        if choice in self.promotion_options:
            new_piece = self.promotion_options[choice](
                self.side, 
                (x * TILESIZE, y * TILESIZE),
                self.board
            )
            self.board.map[y][x] = new_piece
            self.is_promoting = False
            return new_piece
        return None

    def draw_promotion_menu(self):
        """Draw the promotion menu with images"""
        screen = pygame.display.get_surface()        
        menu_width = TILESIZE * 8 
        menu_height = TILESIZE * 2
        menu_surface = pygame.Surface((menu_width, menu_height))
        pygame.draw.rect(menu_surface, (255, 255, 255), menu_surface.get_rect())
        pygame.draw.rect(menu_surface, (0, 0, 0), menu_surface.get_rect(), 2)
        options = [
            ("Q: Queen", queen[self.side]),
            ("R: Rook", rook[self.side]),
            ("B: Bishop", bishop[self.side]),
            ("N: Knight", knight[self.side])
        ]
        for i, (text, image) in enumerate(options):
            piece_x = 20 + (i * (menu_width // 4))
            piece_y = 10
            menu_surface.blit(image, (piece_x, piece_y))
            text_obj = Text(text, 24, COLOR['BLACK'], 
                           (piece_x, piece_y + TILESIZE))
            text_obj.draw(menu_surface)
        screen_rect = screen.get_rect()
        menu_rect = menu_surface.get_rect(center=screen_rect.center)
        screen.blit(menu_surface, menu_rect)
        pygame.display.flip()

    def draw(self, screen):
        """Override the draw method to draw the promotion menu if needed"""
        super().draw(screen)
        if self.is_promoting:
            self.draw_promotion_menu()

    def end_turn(self):
        """Called when the turn ends"""
        self.just_moved_two = False
        self.can_be_captured_en_passant = False
