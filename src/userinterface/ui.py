from config.settings.settings import *
from .text import Text
from .button import Button
from .processbar import ProgressBar

class UI:
    def __init__(self):
        """Initialize UI components"""
        self.loading_bar = ProgressBar(
            position=(400, 450),
            width=400,
            height=40,
            border_color=COLOR['WHITE'],
            fill_color=COLOR['GREEN'],
            border_width=3
        )
        self.restart_button = Button(
            position=(500, 450),
            width=200,
            height=50,
            text=Text("Restart Game", 36, COLOR['BLACK'], (0, 0)),
            color=COLOR['WHITE'],
            hover_color=COLOR['GREY']
        )
        self.turn_text = Text("Current Turn: White", 36, COLOR['WHITE'], (850, 100))
        self.game_over_text = Text("", 74, COLOR['WHITE'], (400, 300))
        self.instructions = [
            ("LEFT CLICK TO MOVE", (10, 800)),
            ("RIGHT CLICK TO DELETE", (10, 830)),
            ("PRESS R TO RESTORE PIECE", (10, 860))
        ]
        self.text_elements = [
            Text(text, 24, COLOR['WHITE'], pos) 
            for text, pos in self.instructions
        ]
        self.ai_progress = ProgressBar(
            position=(850, 200),
            width=300,
            height=30,
            border_color=COLOR['BLACK'],
            fill_color=COLOR['GREEN']
        )

    def handle_events(self, event):
        """Handle UI-related events"""
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.check_hover(mouse_pos)
        if self.restart_button.is_clicked(event):
            return "RESTART"            
        return None

    def update(self, game_state):
        """Update UI elements based on game state"""
        current_turn = "White" if game_state.current_turn == 0 else "Black"
        self.turn_text.update(f"Current Turn: {current_turn}")
        if game_state.game_over:
            winner = "White" if game_state.winner == 0 else "Black"
            self.game_over_text.update(f"{winner} Wins!")
            self.restart_button.set_enabled(True)
        else:
            self.game_over_text.update("")
            self.restart_button.set_enabled(False)
        if game_state.current_turn == 1:  # AI's turn
            self.ai_progress.update()

    def draw(self, screen):
        """Draw all UI elements"""
        for text in self.text_elements:
            text.draw(screen)
        self.turn_text.draw(screen)
        if self.game_over_text.text:
            self.game_over_text.draw(screen)
            self.restart_button.draw(screen)
        self.ai_progress.draw(screen)


