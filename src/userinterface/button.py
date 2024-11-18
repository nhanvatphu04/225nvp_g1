from .text import Text
import pygame
from typing import Tuple, Optional

class Button:
    def __init__(self, 
                 position: Tuple[int, int], 
                 width: int, 
                 height: int, 
                 text: Optional[Text] = None,
                 color: Tuple[int, int, int] = (255, 255, 255),
                 hover_color: Tuple[int, int, int] = (200, 200, 200),
                 image_path: Optional[str] = None):
        """Initialize button with the given properties
        Args:
            position: Position (x, y) of the button
            width: Button width
            height: Button height
            text: Text object containing button content (optional)
            color: Button background color (R,G,B)
            hover_color: Background color when hovered (R,G,B)
            image_path: Path to the image file (optional)
        """
        self.position = position
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.hovered = False
        self.enabled = True
        self.disabled_color = (128, 128, 128)
        self.image = None
        if image_path:
            self._load_image(image_path)
        if text:
            self.text.rect.center = self.rect.center

    def _load_image(self, image_path: str) -> None:
        """Load and scale image to fit the button
        Args:
            image_path: Path to the image file
        """
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error as e:
            print(f"Cannot load image {image_path}: {e}")
            self.image = None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw button on screen
        Args:
            screen: Pygame surface to draw on
        """
        if not self.enabled:
            pygame.draw.rect(screen, self.disabled_color, self.rect)
        else:
            pygame.draw.rect(screen, self.hover_color if self.hovered else self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        if self.image:
            screen.blit(self.image, self.rect)
        if self.text:
            screen.blit(self.text.rendered_text, self.text.rect)

    def check_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Check and update hover state
        Args:
            mouse_pos: Mouse position (x, y)
        """
        if self.enabled:
            self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Check if the button is clicked
        Args:
            event: Pygame event
        Returns:
            bool: True if the button is clicked and enabled
        """
        return (self.enabled and 
                event.type == pygame.MOUSEBUTTONDOWN and 
                self.rect.collidepoint(event.pos))

    def set_enabled(self, enabled: bool) -> None:
        """Set the enabled/disabled state of the button
        Args:
            enabled: True to enable, False to disable
        """
        self.enabled = enabled
