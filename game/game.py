# Full version of the game
from config.settings.settings import *
from src.modules import ChessBoard, UserEvent, King, Queen, Bishop, Knight, Rook, Pawn
from src.userinterface import UI, Text, Button, ProgressBar
from utils.resource_manager import ResourceManager
from game.BasicAI import BasicAI
from game.ProAI import ProAI
import os, threading, sys, random, io
from PIL import Image

class Game:
    def __init__(self):
        pygame.init()
        self.resource_manager = ResourceManager()
        if not os.path.exists('config.json'):
            if not self.resource_manager.select_game_directory():
                sys.exit(1)        
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.title = pygame.display.set_caption("CHESS")
        # Load icon trước
        icon_image = self.resource_manager.load_image(ICON)
        if icon_image:  # Kiểm tra nếu load thành công
            pygame.display.set_icon(icon_image)
        self.game_over_font = self.resource_manager.load_font(None, 74)
        self.restart_font = self.resource_manager.load_font(None, 36)
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
        if self.resource_manager.load_sound(BGMUSIC):
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
        # AI initialization
        self.ai_mode = "Basic"
        self.ai_button = Button(
            position=(850, 50),
            width=200,
            height=40,
            text=Text(f"AI: {self.ai_mode}", 24, COLOR['BLACK'], (0, 0)),
            color=COLOR['WHITE'],
            hover_color=COLOR['LIGHT_GRAY']
        )
        self.ai_difficulty_text = Text(
            f"AI Difficulty: {self.ai_mode}",
            24,
            COLOR['BLACK'],
            (810, 100)
        )
        self.basic_ai = BasicAI()
        self.pro_ai = ProAI()
        self.ai = self.basic_ai
        self.current_turn = 0  # 0: white, 1: black
        for piece in self.all_pieces:
            x, y = piece.get_position()
            self.chessboard.map[y][x] = piece
        self.game_over = False
        self.winner = None  # 0: White wins, 1: Black wins
        self.ai_progress = ProgressBar(
            position=(850, 0),
            width=300,
            height=30,
            border_color=COLOR['BLACK'],
            fill_color=COLOR['GREEN']
        )
        # AI thinking
        self.ai_thinking_time = 0
        self.ai_think_duration = 1000
        self.is_loading = True
        self.ai_thread = None
        self.ai_move_ready = None
        self.ai_is_thinking = False
        self.ai_move_calculated = False
        self.ai_move_result = None
        self.last_ai_move = None
        # Loading
        self.loading_time = 0
        self.loading_duration = 2000
        self.frame_delay = 3
        self.frame_counter = 0

    def load_background(self):
        """Load and convert GIF frames before game starts"""
        try:
            gif = Image.open(os.path.join(self.resource_manager.background_path, BACKGROUND))
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.ai_button.is_clicked(event):
                    if self.ai_mode == "Basic":
                        self.ai_mode = "Pro"
                        self.ai = self.pro_ai
                    else:
                        self.ai_mode = "Basic" 
                        self.ai = self.basic_ai
                    self.ai_button.text.update(f"AI: {self.ai_mode}")
                    self.ai_difficulty_text.update(f"AI Difficulty: {self.ai_mode}")            
            if self.current_turn == 0:
                moved = self.user_event.handleEvent(self.all_pieces, event, self.delete_pieces, self.chessboard)
                if moved:
                    self.current_turn = 1
            self.ai_button.check_hover(pygame.mouse.get_pos())

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
            self.winner = 1
        elif self.blackking.is_captured:
            self.game_over = True
            self.winner = 0
        if not self.game_over:
            if self.current_turn == 1:  # Black's turn (AI)
                self.ai_thinking_time += self.clock.get_time()
                progress = min(self.ai_thinking_time / self.ai_think_duration, 1.0)
                self.ai_progress.set_progress(progress)
                if not self.ai_is_thinking and not self.ai_move_calculated:
                    if not self.ai_thread or not self.ai_thread.is_alive():
                        self.ai_is_thinking = True
                        self.ai_thread = threading.Thread(target=self.process_ai_move)
                        self.ai_thread.start()
                if self.ai_thinking_time >= self.ai_think_duration and self.ai_move_calculated:
                    if self.ai_move_result:
                        piece, (new_x, new_y) = self.ai_move_result
                        old_x, old_y = piece.get_position()
                        target_piece = self.chessboard.map[new_y][new_x]
                        if target_piece is not None:
                            if target_piece.side != piece.side:
                                self.all_pieces.remove(target_piece)
                                target_piece.is_captured = True
                        piece.move(new_x, new_y)
                        self.chessboard.map[old_y][old_x] = None
                        self.chessboard.map[new_y][new_x] = piece
                        self.last_ai_move = ((old_x, old_y), (new_x, new_y))                        
                    self.ai_thinking_time = 0
                    self.current_turn = 0
                    self.ai_move_calculated = False
                    self.ai_move_result = None
                    self.ai_is_thinking = False
            self.whiteking.is_in_check()
            self.blackking.is_in_check()

    def draw(self):
        if not self.bg_loading_complete:
            return
        self.screen.fill(COLOR['WHITE'])
        if self.bg_frames:
            self.screen.blit(self.bg_frames[self.current_frame], (800, 586))
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.bg_frames)
                self.frame_counter = 0
        self.ai_button.draw(self.screen)
        self.ai_difficulty_text.draw(self.screen)
        if self.is_loading:
            loading_text = self.game_over_font.render(self.current_loading_message, True, COLOR['BLACK'])
            text_rect = loading_text.get_rect(center=(SCREENWIDTH//2, SCREENHEIGHT//2 - 50))
            self.screen.blit(loading_text, text_rect)
            self.loading_progress.draw(self.screen)
        else:
            self.chessboard.draw(self.screen)
            self.user_event.draw(self.screen)
            self.draw_last_move()            
            for piece in self.all_pieces:
                piece.draw(self.screen)
            for text in self.text:
                text.draw(self.screen)                
            if self.current_turn == 1:  # Black's turn (AI)
                self.ai_progress.draw(self.screen)
                self.ai_progress.update()                
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

    def reset_game(self):
        """Reset the game to the initial state"""
        current_ai_mode = self.ai_mode
        current_ai = self.ai        
        resource_manager.clear_cache()
        self.is_loading = True
        self.loading_time = 0
        self.game_over = False
        self.winner = None
        self.all_pieces.clear()
        self.delete_pieces.clear()        
        self.chessboard = ChessBoard()
        self.last_ai_move = None
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
        self.ai_mode = current_ai_mode
        self.ai = current_ai
        self.ai_button.text.update(f"AI: {self.ai_mode}")
        self.ai_difficulty_text.update(f"AI Difficulty: {self.ai_mode}")
        self.last_ai_move = None

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
    
    def save_game(self):
        """Save game"""
        game_state = {
            'score': self.score,
            'level': self.level,
            'pieces': self.get_piece_positions(),
        }
        self.resource_manager.save_game(game_state)

    def load_game(self):
        """Load game"""
        game_state = self.resource_manager.load_game()
        if game_state:
            self.score = game_state['score']
            self.level = game_state['level']
            self.load_piece_positions(game_state['pieces'])

    def render_text(self, text, font_key='DEFAULT', color=COLOR['WHITE'], center_pos=None):
        """Render text with specified font"""
        font = self.resource_manager.load_font(FONTS[font_key])
        text_surface = font.render(text, True, color)
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
        
    def draw_last_move(self):
        """Draw the last AI move"""
        if self.last_ai_move:
            from_pos, to_pos = self.last_ai_move
            from_rect = pygame.Rect(
                from_pos[0] * TILESIZE,
                from_pos[1] * TILESIZE,
                TILESIZE,
                TILESIZE
            )
            pygame.draw.rect(self.screen, COLOR['GREEN'], from_rect, 3)            
            to_rect = pygame.Rect(
                to_pos[0] * TILESIZE,
                to_pos[1] * TILESIZE,
                TILESIZE,
                TILESIZE
            )
            pygame.draw.rect(self.screen, COLOR['GREEN'], to_rect, 3)

    def show_settings(self):
        """Show settings menu"""
        if self.resource_manager.select_game_directory():
            self.load_resources()

    def process_ai_move(self):
        """Process AI move in separate thread"""
        self.ai_move_result = self.ai.make_move(self.all_pieces, self.chessboard)
        self.ai_move_calculated = True
        self.ai_is_thinking = False