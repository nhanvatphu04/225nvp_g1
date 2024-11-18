import random

class BasicAI:
    """
    Basic AI implementation for chess game.
    """
    
    def __init__(self, side=1):
        """
        Initialize AI with given side (1: black, 0: white)
        """
        self.side = side
        self._init_piece_values()
    
    def _init_piece_values(self):
        """
        Initialize the values for each piece type
        """
        self.piece_values = {
            'King': 900,
            'Queen': 90,
            'Rook': 50,
            'Bishop': 30,
            'Knight': 30,
            'Pawn': 10
        }

    def evaluate_board(self, pieces):
        """
        Calculate the total score of the current board state
        """
        score = 0
        for piece in pieces:
            value = self.piece_values[piece.__class__.__name__]
            if piece.side == self.side:
                score += value
            else:
                score -= value
        return score

    def get_all_possible_moves(self, pieces, chessboard):
        """
        Get all possible moves for the current side
        """
        moves = []
        for piece in pieces:
            if piece.side == self.side and not piece.is_captured:
                possible_moves = piece.get_possible_moves(chessboard)
                for move in possible_moves:
                    moves.append((piece, move))
        return moves

    def make_move(self, pieces, chessboard):
        """
        Select and return the best move based on board evaluation
        """
        possible_moves = self.get_all_possible_moves(pieces, chessboard)
        if not possible_moves:
            return None
            
        return self._find_best_move(possible_moves, pieces, chessboard)
    
    def _find_best_move(self, possible_moves, pieces, chessboard):
        """
        Find the move with the highest evaluation score
        """
        best_move = None
        best_score = float('-inf')
        
        for piece, move in possible_moves:
            score = self._evaluate_move(piece, move, pieces, chessboard)
            if score > best_score:
                best_score = score
                best_move = (piece, move)
                
        return best_move
    
    def _evaluate_move(self, piece, move, pieces, chessboard):
        """
        Evaluate a single move by simulating it
        """
        old_x, old_y = piece.get_position()
        old_piece_at_target = chessboard.map[move[1]][move[0]]

        piece.move(move[0], move[1])
        score = self.evaluate_board(pieces)

        if old_piece_at_target is not None:
            score += self.piece_values[old_piece_at_target.__class__.__name__]

        piece.move(old_x, old_y)
        if old_piece_at_target:
            chessboard.map[move[1]][move[0]] = old_piece_at_target
            old_piece_at_target.is_captured = False
            
        return score