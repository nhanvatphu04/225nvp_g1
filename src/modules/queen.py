from config.settings.settings import *
from ..modules import Piece

queen[0] = scale2x(queen[0])
queen[1] = scale2x(queen[1])

class Queen(Piece):
    def __init__(self, side, position, board):
        """
        side 0 = White   
        side 1 = Black
        """
        image = queen[0] if side == 0 else queen[1]
        super().__init__(image, side, position, board)
    
    def get_possible_moves(self, chessboard=None):
        moves = []
        x, y = self.get_position()
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
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
        
    def move(self, x, y):
        old_x, old_y = self.get_position()
        self.board.map[old_y][old_x] = None
        self.board.map[y][x] = self
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.pos = (x, y)
        self.last_position = (self.rect.x, self.rect.y)