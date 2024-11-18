# Simple version of the game
from config.settings.settings import *
from src.modules import ChessBoard, UserEvent, King, Queen, Bishop, Knight, Rook, Pawn
from src.userinterface import UI, Text, Button
from game.ai import ChessAI
import os, threading

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.title = pygame.display.set_caption("CHESS")
        self.icon = pygame.display.set_icon(ICON)
        self.chessboard = ChessBoard()
        self.user_event = UserEvent()
        self.running = True
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load(BGMUSIC)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        # Text
        instructions = [
            ("LEFT CLICK TO MOVE", (10, 800)),
            ("RIGHT CLICK TO DELETE", (10, 830)),
            ("PRESS R TO RESTORE PIECE", (10, 860))
        ]
        self.text = [Text(text, 24, COLOR['BLACK'], pos) for text, pos in instructions]
        # White side
        self.whiteking = King(0, boardset['e1'], self.chessboard)
        self.whitequeen = Queen(0, boardset['d1'], self.chessboard)
        self.whitebishops = [
            Bishop(0, boardset['c1'], self.chessboard),
            Bishop(0, boardset['f1'], self.chessboard)
        ]
        self.whiteknights = [
            Knight(0, boardset['b1'], self.chessboard),
            Knight(0, boardset['g1'], self.chessboard)
        ]
        self.whiterooks = [
            Rook(0, boardset['a1'], self.chessboard),
            Rook(0, boardset['h1'], self.chessboard)
        ]
        self.whitepawns = [
            Pawn(0, boardset[f'{chr(97+i)}2'], self.chessboard) 
            for i in range(8)
        ]
        # Black side
        self.blackking = King(1, boardset['e8'], self.chessboard)
        self.blackqueen = Queen(1, boardset['d8'], self.chessboard)
        self.blackbishops = [
            Bishop(1, boardset['c8'], self.chessboard),
            Bishop(1, boardset['f8'], self.chessboard)
        ]
        self.blackknights = [
            Knight(1, boardset['b8'], self.chessboard),
            Knight(1, boardset['g8'], self.chessboard)
        ]
        self.blackrooks = [
            Rook(1, boardset['a8'], self.chessboard),
            Rook(1, boardset['h8'], self.chessboard)
        ]
        self.blackpawns = [
            Pawn(1, boardset[f'{chr(97+i)}7'], self.chessboard) 
            for i in range(8)
        ]
        # All pieces
        self.all_pieces = [
            self.whiteking,
            self.whitequeen,
            *self.whitebishops,
            *self.whiteknights,
            *self.whiterooks,
            *self.whitepawns,
            self.blackking,
            self.blackqueen,
            *self.blackbishops,
            *self.blackknights,
            *self.blackrooks,
            *self.blackpawns
        ]
        self.delete_pieces = []
        # UI
        self.ai = ChessAI()
        self.current_turn = 0  # 0: white, 1: black
        for piece in self.all_pieces:
            x, y = piece.get_position()
            self.chessboard.map[y][x] = piece
        self.game_over = False
        self.winner = None  # 0: White wins, 1: Black wins
        self.game_over_font = pygame.font.Font(None, 74)
        self.restart_font = pygame.font.Font(None, 36)

    def handle_events(self):
        """Handle events from the user"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
                elif event.key in [pygame.K_q, pygame.K_r, pygame.K_b, pygame.K_n]:
                    for piece in self.all_pieces:
                        if isinstance(piece, Pawn) and piece.is_promoting:
                            new_piece = piece.promote(event.key)
                            if new_piece:
                                self.all_pieces.remove(piece)
                                self.all_pieces.append(new_piece)
                                break
            elif self.current_turn == 0:
                moved = self.user_event.handleEvent(self.all_pieces, event, self.delete_pieces, self.chessboard)
                if moved:
                    self.current_turn = 1

    def update(self):
        """Update the game state"""
        if self.whiteking.is_captured:
            self.game_over = True
            self.winner = 1  # Black wins
        elif self.blackking.is_captured:
            self.game_over = True
            self.winner = 0  # White wins        
        if not self.game_over:
            if self.current_turn == 1:  # Black's turn (AI)
                ai_move = self.ai.make_move(self.all_pieces, self.chessboard)
                if ai_move:
                    piece, (new_x, new_y) = ai_move
                    if (new_x, new_y) in piece.get_possible_moves(self.chessboard):
                        target_piece = self.chessboard.map[new_y][new_x]
                        if target_piece is not None:
                            if target_piece.side != piece.side:
                                self.all_pieces.remove(target_piece)
                                target_piece.is_captured = True                        
                        piece.move(new_x, new_y)
                        self.whiteking.is_in_check()
                        self.blackking.is_in_check()
                        self.current_turn = 0
            else:
                self.whiteking.is_in_check()
                self.blackking.is_in_check()

    def draw(self):
        """Draw everything to the screen"""
        self.screen.fill(COLOR['WHITE'])
        self.chessboard.draw(self.screen)
        self.user_event.draw(self.screen)        
        for piece in self.all_pieces:
            piece.draw(self.screen)
        for text in self.text:
            text.draw(self.screen)
        if self.game_over:
            overlay = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            winner_text = "White Wins!" if self.winner == 0 else "Black Wins!"
            text_surface = self.game_over_font.render(winner_text, True, (255, 215, 0))
            text_rect = text_surface.get_rect(center=(SCREENWIDTH // 2, SCREENHEIGHT // 2 - 50))
            self.screen.blit(text_surface, text_rect)
            restart_text = "Press SPACE to play again or ESC to quit"
            restart_surface = self.restart_font.render(restart_text, True, (255, 255, 255))
            restart_rect = restart_surface.get_rect(center=(SCREENWIDTH // 2, SCREENHEIGHT // 2 + 50))
            self.screen.blit(restart_surface, restart_rect)
        pygame.display.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.mixer.music.stop()
        pygame.quit()

    def delete_pieces(self, piece):
        if piece in self.all_pieces:
            piece.is_captured = True
            x, y = piece.pos
            self.chessboard.map[y][x] = None

    def is_check(self, side):
        king = self.whiteking if side == 0 else self.blackking
        return king.is_in_check()

    def is_checkmate(self, side):
        if not self.is_check(side):
            return False
        pieces = [p for p in self.all_pieces if p.side == side and not p.is_captured]
        for piece in pieces:
            moves = piece.get_possible_moves(self.chessboard)
            for move in moves:
                old_pos = piece.get_position()
                piece.move(move[0], move[1])
                still_in_check = self.is_check(side)
                piece.move(old_pos[0], old_pos[1])
                if not still_in_check:
                    return False
        return True

    def reset_game(self):
        """Reset the game to the initial state"""
        self.game_over = False
        self.winner = None
        self.all_pieces.clear()
        self.delete_pieces.clear()        
        self.chessboard = ChessBoard()
        # White side
        self.whiteking = King(0, boardset['e1'], self.chessboard)
        self.whitequeen = Queen(0, boardset['d1'], self.chessboard)
        self.whitebishops = [
            Bishop(0, boardset['c1'], self.chessboard),
            Bishop(0, boardset['f1'], self.chessboard)
        ]
        self.whiteknights = [
            Knight(0, boardset['b1'], self.chessboard),
            Knight(0, boardset['g1'], self.chessboard)
        ]
        self.whiterooks = [
            Rook(0, boardset['a1'], self.chessboard),
            Rook(0, boardset['h1'], self.chessboard)
        ]
        self.whitepawns = [
            Pawn(0, boardset[f'{chr(97+i)}2'], self.chessboard) 
            for i in range(8)
        ]
        # Black side
        self.blackking = King(1, boardset['e8'], self.chessboard)
        self.blackqueen = Queen(1, boardset['d8'], self.chessboard)
        self.blackbishops = [
            Bishop(1, boardset['c8'], self.chessboard),
            Bishop(1, boardset['f8'], self.chessboard)
        ]
        self.blackknights = [
            Knight(1, boardset['b8'], self.chessboard),
            Knight(1, boardset['g8'], self.chessboard)
        ]
        self.blackrooks = [
            Rook(1, boardset['a8'], self.chessboard),
            Rook(1, boardset['h8'], self.chessboard)
        ]
        self.blackpawns = [
            Pawn(1, boardset[f'{chr(97+i)}7'], self.chessboard) 
            for i in range(8)
        ]
        self.all_pieces = [
            self.whiteking,
            self.whitequeen,
            *self.whitebishops,
            *self.whiteknights,
            *self.whiterooks,
            *self.whitepawns,
            self.blackking,
            self.blackqueen,
            *self.blackbishops,
            *self.blackknights,
            *self.blackrooks,
            *self.blackpawns
        ]
        self.current_turn = 0
        for piece in self.all_pieces:
            x, y = piece.get_position()
            self.chessboard.map[y][x] = piece
