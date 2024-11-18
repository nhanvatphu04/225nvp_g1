from config.settings.settings import *
from ..modules import Piece
from .rook import Rook
from .pawn import Pawn
from .knight import Knight
from .bishop import Bishop
from .queen import Queen
import pygame
import math

king[0] = scale2x(king[0])
king[1] = scale2x(king[1])

class King(Piece):
    def __init__(self, side, position, board):
        """
        side 0 = White   
        side 1 = Black
        """
        image = king[0] if side == 0 else king[1]
        super().__init__(image, side, position, board)
        self.first_move = True
        self.in_check = False
        self.check_warning_color = (255, 0, 0, 128)
    
    def get_possible_moves(self, chessboard=None):
        moves = []
        x, y = self.get_position()
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]        
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            if self.is_valid_position(new_x, new_y):
                target_piece = self.board.map[new_y][new_x]
                if target_piece is None or target_piece.side != self.side:
                    moves.append((new_x, new_y))        
        # Add castle logic
        if self.first_move and not self.is_in_check():
            # Short castle (right side)
            if self.can_castle_kingside():
                moves.append((x + 2, y))  # Move king 2 squares to the right            
            # Long castle (left side)
            if self.can_castle_queenside():
                moves.append((x - 2, y))  # Move king 2 squares to the left        
        return moves
    
    def move(self, x, y):
        """Move king to a new position"""
        old_x, old_y = self.get_position()
        if abs(x - old_x) == 2:
            # Short castle
            if x > old_x:
                rook = self.board.map[old_y][7]  # Get the rook on the right
                if isinstance(rook, Rook):
                    rook.move(old_x + 1, old_y)  # Move the rook
            # Long castle
            else:
                rook = self.board.map[old_y][0]  # Get the rook on the left
                if isinstance(rook, Rook):
                    rook.move(old_x - 1, old_y)  # Move the rook
        self.board.map[old_y][old_x] = None
        target_piece = self.board.map[y][x]
        if target_piece is not None:
            target_piece.is_captured = True            
        self.board.map[y][x] = self
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.pos = (x, y)
        self.last_position = (self.rect.x, self.rect.y)        
        self.first_move = False
        self.is_in_check()
    
    def _can_piece_attack(self, piece, target_x, target_y):
        """Check if a piece can attack the position (x,y)"""
        piece_x = piece.rect.x // TILESIZE
        piece_y = piece.rect.y // TILESIZE
        if isinstance(piece, Pawn):
            direction = 1 if piece.side == 1 else -1
            return (abs(piece_x - target_x) == 1 and 
                    (piece_y + direction) == target_y)                
        elif isinstance(piece, Knight):
            dx = abs(piece_x - target_x)
            dy = abs(piece_y - target_y)
            return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)        
        elif isinstance(piece, (Rook, Queen)):
            if piece_x == target_x or piece_y == target_y:
                return self._is_path_clear(piece_x, piece_y, target_x, target_y)            
        if isinstance(piece, (Bishop, Queen)):
            if abs(piece_x - target_x) == abs(piece_y - target_y):
                return self._is_path_clear(piece_x, piece_y, target_x, target_y)            
        return False
    
    def _is_path_clear(self, start_x, start_y, end_x, end_y):
        """Check if the path is blocked"""
        dx = 0 if start_x == end_x else (end_x - start_x) // abs(end_x - start_x)
        dy = 0 if start_y == end_y else (end_y - start_y) // abs(end_y - start_y)        
        current_x = start_x + dx
        current_y = start_y + dy        
        while (current_x, current_y) != (end_x, end_y):
            if self.board.map[current_y][current_x] is not None:
                return False
            current_x += dx
            current_y += dy        
        return True
    
    def can_castle_kingside(self):
        """Check if the king can castle kingside"""
        if not self.first_move:
            return False        
        x, y = self.get_position()
        rook_x = 7
        rook = self.board.map[y][rook_x]
        if (isinstance(rook, Rook) and 
            rook.side == self.side and 
            rook.first_move):
            for i in range(x + 1, rook_x):
                if self.board.map[y][i] is not None:
                    return False
            for i in range(x, x + 3):
                if self.is_square_attacked(i, y):
                    return False
            return True
        return False
    
    def can_castle_queenside(self):
        """Check if the long castle is possible"""
        if not self.first_move:
            return False        
        x, y = self.get_position()
        rook_x = 0
        rook = self.board.map[y][rook_x]
        # Check long castle condition
        if (isinstance(rook, Rook) and 
            rook.side == self.side and 
            rook.first_move):
            # Check if there is no piece blocking the king and the rook
            for i in range(rook_x + 1, x):
                if self.board.map[y][i] is not None:
                    return False
            # Check if the king's path is not attacked
            for i in range(x - 2, x + 1):
                if self.is_square_attacked(i, y):
                    return False
            return True
        return False
    
    def is_square_attacked(self, x, y):
        """Check if the position (x,y) is attacked"""
        original_x = self.rect.x
        original_y = self.rect.y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        is_attacked = self.is_in_check()
        self.rect.x = original_x
        self.rect.y = original_y        
        return is_attacked
    
    def is_in_check(self):
        """Check if the king is in check"""
        x = self.rect.x // TILESIZE
        y = self.rect.y // TILESIZE
        for row in range(8):
            for col in range(8):
                piece = self.board.map[row][col]
                if piece and piece.side != self.side:
                    if self._can_piece_attack(piece, x, y):
                        self.in_check = True
                        return True
        self.in_check = False
        return False
    
    def draw(self, screen):
        """Draw the king and the warning effect when in check"""
        super().draw(screen)        
        if self.in_check:
            current_time = pygame.time.get_ticks()
            alpha = abs(math.sin(current_time * 0.005)) * 255
            warning_surface = pygame.Surface((TILESIZE + 6, TILESIZE + 6), pygame.SRCALPHA)
            pygame.draw.rect(warning_surface, (255, 0, 0, int(alpha)), 
                            warning_surface.get_rect(), 3)
            center = (TILESIZE // 2, TILESIZE // 2)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                end_x = center[0] + math.cos(rad) * (TILESIZE // 2)
                end_y = center[1] + math.sin(rad) * (TILESIZE // 2)
                pygame.draw.line(warning_surface, (255, 0, 0, int(alpha * 0.7)),
                               center, (end_x, end_y), 2)
            warning_pos = (self.rect.x - 3, self.rect.y - 3)
            screen.blit(warning_surface, warning_pos)