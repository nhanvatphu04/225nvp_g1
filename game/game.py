# Full version of the game
from config.settings.settings import *
from src.modules import ChessBoard, UserEvent, King, Queen, Bishop, Knight, Rook, Pawn
from src.userinterface import UI, Text, Button, ProgressBar
from game.ai import ChessAI
import os, threading, sys
import random
from PIL import Image
import io
from utils.resource_manager import ResourceManager

class Game:
    def __init__(self):
        pygame.init()
        self.resource_manager = ResourceManager()
        
        # Cho phép người dùng chọn thư mục khi khởi động game lần đầu
        if not os.path.exists('config.json'):
            if not self.resource_manager.select_game_directory():
                sys.exit(1)
        
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.title = pygame.display.set_caption("CHESS")
        self.icon = pygame.display.set_icon(ICON)
        self.game_over_font = resource_manager.load_font(None, 74)
        self.restart_font = resource_manager.load_font(None, 36)
        self.loading_progress = ProgressBar(
            position=(SCREENWIDTH//2 - 200, SCREENHEIGHT//2),
            width=400,
            height=40,
            border_color=COLOR['BLACK'],
            fill_color=COLOR['BLUE']
        )
        self.loading_messages = [
            "Preparing the board...",
            "Arranging pieces...",
            "Starting AI...",
            "Loading resources...",
            "Getting ready...",
            "Loading background animation...",
            "Processing frames..."
        ]
        self.current_loading_message = random.choice(self.loading_messages)
        self.bg_frames = []
        self.current_frame = 0
        self.bg_loading_complete = False
        self.load_background()
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
        self.ai = ChessAI()
        self.current_turn = 0  # 0: white, 1: black
        for piece in self.all_pieces:
            x, y = piece.get_position()
            self.chessboard.map[y][x] = piece
        self.game_over = False
        self.winner = None  # 0: White wins, 1: Black wins
        self.ai_progress = ProgressBar(
            position=(850, 200),
            width=300,
            height=30,
            border_color=COLOR['BLACK'],
            fill_color=COLOR['GREEN']
        )
        self.ai_thinking_time = 0
        self.ai_think_duration = 1000
        self.is_loading = True
        self.loading_time = 0
        self.loading_duration = 2000
        self.frame_delay = 3
        self.frame_counter = 0

    def load_background(self):
        """Load and convert GIF frames before game starts"""
        try:
            gif = Image.open(BACKGROUND)
            total_frames = 0
            while True:
                try:
                    gif.seek(total_frames)
                    total_frames += 1
                except EOFError:
                    break
            gif.seek(0)            
            while True:
                try:
                    gif.seek(self.current_frame)
                    frame = gif.convert('RGBA')
                    pygame_image = pygame.image.fromstring(
                        frame.tobytes(), frame.size, frame.mode
                    )
                    self.bg_frames.append(pygame_image)
                    self.current_frame += 1
                    progress = min(self.current_frame / total_frames, 1.0)
                    self.loading_progress.set_progress(progress)
                    self.current_loading_message = f"Loading background: {int(progress * 100)}%"
                    self.screen.fill(COLOR['WHITE'])
                    loading_text = self.game_over_font.render(self.current_loading_message, True, COLOR['BLACK'])
                    text_rect = loading_text.get_rect(center=(SCREENWIDTH//2, SCREENHEIGHT//2 - 50))
                    self.screen.blit(loading_text, text_rect)
                    self.loading_progress.draw(self.screen)
                    pygame.display.update()
                except EOFError:
                    self.bg_loading_complete = True
                    break
            self.current_frame = 0
        except Exception as e:
            self.bg_frames = []
            self.bg_loading_complete = True

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
        if not self.bg_loading_complete:
            return            
        if self.is_loading:
            self.loading_time += self.clock.get_time()
            progress = min(self.loading_time / self.loading_duration, 1.0)
            self.loading_progress.set_progress(progress)            
            if self.loading_time >= self.loading_duration:
                self.is_loading = False
                self.loading_time = 0
            return            
        if self.whiteking.is_captured:
            self.game_over = True
            self.winner = 1  # Black wins
        elif self.blackking.is_captured:
            self.game_over = True
            self.winner = 0  # White wins        
        if not self.game_over:
            if self.current_turn == 1:  # Black's turn (AI)
                self.ai_thinking_time += self.clock.get_time()
                progress = min(self.ai_thinking_time / self.ai_think_duration, 1.0)
                self.ai_progress.set_progress(progress)
                if self.ai_thinking_time >= self.ai_think_duration:
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
                    self.ai_thinking_time = 0
                    self.current_turn = 0
            else:
                self.whiteking.is_in_check()
                self.blackking.is_in_check()

    def draw(self):
        """Draw everything on the screen"""
        if not self.bg_loading_complete:
            return
        self.screen.fill(COLOR['WHITE'])
        if self.bg_frames:
            self.screen.blit(self.bg_frames[self.current_frame], (800, 0))
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.bg_frames)
                self.frame_counter = 0
        
        if self.is_loading:
            loading_text = self.game_over_font.render(self.current_loading_message, True, COLOR['BLACK'])
            text_rect = loading_text.get_rect(center=(SCREENWIDTH//2, SCREENHEIGHT//2 - 50))
            self.screen.blit(loading_text, text_rect)
            self.loading_progress.draw(self.screen)
        else:
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
            if self.current_turn == 1:  # Black's turn (AI)
                self.ai_progress.draw(self.screen)
                self.ai_progress.update()
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
        resource_manager.clear_cache()
        self.is_loading = True
        self.loading_time = 0
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

    def render_text(self, text, font_key='DEFAULT', color=COLOR['WHITE'], center_pos=None):
        """Render text with specified font"""
        text_surface = FONTS[font_key].render(text, True, color)
        if center_pos:
            text_rect = text_surface.get_rect(center=center_pos)
            self.screen.blit(text_surface, text_rect)
        return text_surface

    def draw_menu(self):
        title = self.render_text("CHESS GAME", 'TITLE', COLOR['WHITE'], 
                               (SCREENWIDTH//2, 100))        
        start_text = self.render_text("Press SPACE to Start", 'MENU', COLOR['WHITE'],
                                    (SCREENWIDTH//2, SCREENHEIGHT//2))        
        score = self.render_text(f"Score: {self.score}", 'GAME', COLOR['WHITE'],
                               (50, 30))

    def save_game(self):
        """Lưu game"""
        game_state = {
            'score': self.score,
            'level': self.level,
            'pieces': self.get_piece_positions(),
            # ... other game state data ...
        }
        self.resource_manager.save_game(game_state)

    def load_game(self):
        """Load game"""
        game_state = self.resource_manager.load_game()
        if game_state:
            self.score = game_state['score']
            self.level = game_state['level']
            self.load_piece_positions(game_state['pieces'])
            # ... load other game state data ...

    def show_settings(self):
        """Hiển thị menu cài đặt"""
        if self.resource_manager.select_game_directory():
            # Reload resources if needed
            self.load_resources()
