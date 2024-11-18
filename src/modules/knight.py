from config.settings.settings import *
from ..modules import Piece

knight[0] = scale2x(knight[0])
knight[1] = scale2x(knight[1])

class Knight(Piece):
    def __init__(self, side, position, board):
        """
        side 0 = White   
        side 1 = Black
        """
        image = knight[0] if side == 0 else knight[1]
        super().__init__(image, side, position, board)
    
    def move(self, x, y):
        old_x, old_y = self.get_position()
        self.board.map[old_y][old_x] = None
        self.board.map[y][x] = self
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.pos = (x, y)
        self.last_position = (self.rect.x, self.rect.y)
    
    def get_possible_moves(self, chessboard=None):
        moves = []
        x, y = self.get_position()
        possible_moves = [
            (x+2, y+1), (x+2, y-1),
            (x-2, y+1), (x-2, y-1),
            (x+1, y+2), (x+1, y-2),
            (x-1, y+2), (x-1, y-2)
        ]        
        for move_x, move_y in possible_moves:
            if self.is_valid_position(move_x, move_y):
                target_piece = self.board.map[move_y][move_x]
                if target_piece is None or target_piece.side != self.side:
                    moves.append((move_x, move_y))        
        return moves