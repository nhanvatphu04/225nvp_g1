import random

class ProAI:
    def __init__(self, side=1):
        self.side = side
        self._init_piece_values()
        self._init_position_tables()

    def _init_piece_values(self):
        self.piece_values = {
            'King': 1000,
            'Queen': 180,
            'Rook': 90,
            'Bishop': 65,
            'Knight': 65,
            'Pawn': 20
        }
    
    def _init_position_tables(self):
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        self.rook_table = [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  5,  0,  0,  0]
        ]

    def make_move(self, pieces, chessboard):
        possible_moves = self.get_all_possible_moves(pieces, chessboard)
        if not possible_moves:
            return None
        
        moves_with_scores = []
        king = next((p for p in pieces if p.__class__.__name__ == 'King' and p.side == self.side), None)
        
        is_in_check = king and king.is_in_check()
        
        for piece, move in possible_moves:
            old_x, old_y = piece.get_position()
            old_piece_at_target = chessboard.map[move[1]][move[0]]            

            piece.move(move[0], move[1])
            score = self.evaluate_board(pieces, chessboard)

            if is_in_check:
                if not king.is_in_check():
                    score += 1000

            if king.is_in_check():
                score -= 2000

            if old_piece_at_target:
                capture_bonus = self.piece_values[old_piece_at_target.__class__.__name__] * 0.7
                score += capture_bonus

            piece.move(old_x, old_y)
            if old_piece_at_target:
                chessboard.map[move[1]][move[0]] = old_piece_at_target

            if random.random() < 0.1:
                score += random.randint(-5, 5)
                
            moves_with_scores.append((score, (piece, move)))

        moves_with_scores.sort(key=lambda x: x[0], reverse=True)
        
        if is_in_check:
            valid_moves = []
            for score, move in moves_with_scores:
                piece, (new_x, new_y) = move
                old_x, old_y = piece.get_position()
                old_piece_at_target = chessboard.map[new_y][new_x]
                
                piece.move(new_x, new_y)
                if not king.is_in_check():
                    valid_moves.append((score, move))
                piece.move(old_x, old_y)
                if old_piece_at_target:
                    chessboard.map[new_y][new_x] = old_piece_at_target
                
            if valid_moves:
                moves_with_scores = valid_moves
        
        top_moves = moves_with_scores[:7]
        
        if top_moves:
            weights = [0.35, 0.25, 0.15, 0.1, 0.08, 0.05, 0.02]
            return random.choices(top_moves, weights=weights[:len(top_moves)])[0][1]
        return None

    def get_all_possible_moves(self, pieces, chessboard):
        """Get all possible moves for the AI's pieces"""
        moves = []
        for piece in pieces:
            if piece.side == self.side and not piece.is_captured:
                possible_moves = piece.get_possible_moves(chessboard)
                for move in possible_moves:
                    moves.append((piece, move))
        return moves

    def evaluate_board(self, pieces, chessboard):
        score = 0
        our_pieces = sum(1 for p in pieces if p.side == self.side and not p.is_captured)
        enemy_pieces = sum(1 for p in pieces if p.side != self.side and not p.is_captured)
        
        for piece in pieces:
            if piece.is_captured:
                continue

            value = self.piece_values[piece.__class__.__name__]
            multiplier = 1 if piece.side == self.side else -1
            x, y = piece.get_position()

            score += value * multiplier

            position_value = self.evaluate_position(piece, x, y) * 0.8
            score += position_value * multiplier

            protection_count = self.is_protected(piece, pieces, chessboard)
            protection_value = protection_count * 8
            score += protection_value * multiplier

            attack_value = self.is_attacking(piece, pieces, chessboard)
            score += attack_value * multiplier

            center_control = self.control_center(piece, x, y)
            score += center_control * multiplier

            development = self.evaluate_development(piece, x, y)
            score += development * multiplier

            if piece.__class__.__name__ == 'King':
                if piece.is_in_check():
                    score += 150 if piece.side != self.side else -150
                if piece.side == self.side and piece.first_move:
                    score -= 30
            elif piece.__class__.__name__ == 'Queen':
                if (piece.side == 0 and y < 2) or (piece.side == 1 and y > 5):
                    score -= 20 * multiplier
            elif piece.__class__.__name__ == 'Pawn':
                progress = 7 - y if piece.side == self.side else y
                score += progress * 5 * multiplier
                pawns_in_file = sum(1 for p in pieces 
                                  if not p.is_captured and p.__class__.__name__ == 'Pawn' 
                                  and p.get_position()[0] == x and p.side == piece.side)
                if pawns_in_file > 1:
                    score -= 10 * multiplier

        total_pieces = our_pieces + enemy_pieces
        if total_pieces < 10:
            score *= 1.2

        return score

    def evaluate_position(self, piece, x, y):
        """Evaluate the value of the piece's position"""
        piece_type = piece.__class__.__name__
        if piece_type == 'Pawn':
            return self.pawn_table[y][x] if piece.side == 0 else self.pawn_table[7-y][x]
        elif piece_type == 'Knight':
            return self.knight_table[y][x] if piece.side == 0 else self.knight_table[7-y][x]
        elif piece_type == 'Bishop':
            return self.bishop_table[y][x] if piece.side == 0 else self.bishop_table[7-y][x]
        elif piece_type == 'Queen':
            return self.queen_table[y][x] if piece.side == 0 else self.queen_table[7-y][x]
        elif piece_type == 'Rook':
            return self.rook_table[y][x] if piece.side == 0 else self.rook_table[7-y][x]
        return 0

    def evaluate_development(self, piece, x, y):
        """Evaluate the development of the piece"""
        development_score = 0
        if piece.__class__.__name__ in ['Knight', 'Bishop']:
            if piece.side == 0 and y > 1:  # White
                development_score += 10
            elif piece.side == 1 and y < 6:  # Black
                development_score += 10
        return development_score

    def is_protected(self, piece, pieces, chessboard):
        """Check if the piece is protected and by how many pieces"""
        protection_count = 0
        x, y = piece.get_position()
        for other in pieces:
            if other.side == piece.side and other != piece and not other.is_captured:
                possible_moves = other.get_possible_moves(chessboard)
                if (x, y) in possible_moves:
                    protection_count += 1
        return protection_count
    
    def is_attacking(self, piece, pieces, chessboard):
        """Evaluate the attacking ability of a piece"""
        attack_score = 0
        possible_moves = piece.get_possible_moves(chessboard)
        for x, y in possible_moves:
            if 0 <= x < 8 and 0 <= y < 8:
                target = chessboard.map[y][x]
                if target and target.side != piece.side:
                    attack_score += self.piece_values[target.__class__.__name__] * 0.1
        return attack_score
    
    def control_center(self, piece, x, y):
        """Evaluate the control of the center"""
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        center_control = 0
        if (x, y) in center_squares:
            center_control += 15
        elif 2 <= x <= 5 and 2 <= y <= 5:
            center_control += 8
        return center_control