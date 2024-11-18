import pygame
from typing import Tuple, Optional

class ProgressBar:
    def __init__(self, 
                 position: Tuple[int, int],
                 width: int,
                 height: int,
                 border_color: Tuple[int, int, int] = (255, 255, 255),
                 fill_color: Tuple[int, int, int] = (0, 255, 0),
                 border_width: int = 2):
        """Initialize progress bar
        Args:
            position: Position (x, y) of the progress bar
            width: Progress bar width
            height: Progress bar height
            border_color: Border color (R,G,B)
            fill_color: Progress bar fill color (R,G,B) 
            border_width: Border width
        """
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.border_color = border_color
        self.fill_color = fill_color
        self.border_width = border_width
        self.progress = 0.0
        self.target_progress = 0.0
        self.animation_speed = 0.02

    def set_progress(self, progress):
        """Set progress value between 0.0 and 1.0"""
        self.progress = max(0.0, min(1.0, progress))

    def update(self) -> None:
        """Update progress bar animation"""
        if self.progress < self.target_progress:
            self.progress = min(self.progress + self.animation_speed, self.target_progress)
        elif self.progress > self.target_progress:
            self.progress = max(self.progress - self.animation_speed, self.target_progress)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw progress bar
        Args:
            screen: Pygame surface to draw on
        """
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        if self.progress > 0:
            fill_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                self.rect.width * self.progress,
                self.rect.height
            )
            pygame.draw.rect(screen, self.fill_color, fill_rect)
