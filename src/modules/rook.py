from config.settings.settings import *
from ..modules import Piece

rook[0] = scale2x(rook[0])
rook[1] = scale2x(rook[1])

class Rook(Piece):
    def __init__(self, side, position, board):
        """
        side 0 = White   
        side 1 = Black
        """
        image = rook[0] if side == 0 else rook[1]
        super().__init__(image, side, position, board)
        self.first_move = True
    
    def can_castle(self):
        """Check if the rook can castle"""
        if not self.first_move:
            return False
        x, y = self.get_position()
        if self.side == 0:
            return y == 7 and (x == 0 or x == 7)
        else:
            return y == 0 and (x == 0 or x == 7)
    
    def get_possible_moves(self, chessboard=None):
        moves = []
        x, y = self.get_position()
        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]
        for dx, dy in directions:
            current_x, current_y = x, y
            while True:
                current_x += dx
                current_y += dy
                if not self.is_valid_position(current_x, current_y):
                    break
                target_piece = self.board.map[current_y][current_x]
                if target_piece is None:
                    moves.append((current_x, current_y))
                    continue
                if target_piece.side != self.side:
                    moves.append((current_x, current_y))
                    break
                break        
        return moves
        
    def move(self, new_position, board):
        """Override the move method to update first_move"""
        super().move(new_position, board)
        self.first_move = False