import pygame
from PIL import Image
import os
from config.settings.settings import *

class Background:
    def __init__(self, file_path):
        """Initialize background from gif or image file
        Args:
            file_path: Path to the background file
        """
        self.file_path = file_path
        self.frames = []
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 1000 // FPS
        if file_path.endswith('.gif'):
            self._load_gif()
        else:
            self._load_image()
            
    def _load_gif(self):
        """Load and process gif file"""
        gif = Image.open(self.file_path)
        
        for frame_index in range(gif.n_frames):
            gif.seek(frame_index)
            if gif.mode != 'RGBA':
                frame = gif.convert('RGBA')
            else:
                frame = gif
            frame = frame.resize((SCREENWIDTH, SCREENHEIGHT))
            frame_str = frame.tobytes()
            pygame_frame = pygame.image.fromstring(
                frame_str, frame.size, frame.mode
            )
            self.frames.append(pygame_frame)
            
    def _load_image(self):
        """Load single image file"""
        image = pygame.image.load(self.file_path).convert_alpha()
        scaled_image = pygame.transform.scale(image, (SCREENWIDTH, SCREENHEIGHT))
        self.frames.append(scaled_image)
        
    def update(self):
        """Update current frame of the background"""
        if len(self.frames) > 1:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update > self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_update = current_time
                
    def draw(self, screen):
        """Draw background on screen
        Args:
            screen: Pygame surface to draw on
        """
        screen.blit(self.frames[self.current_frame], (0, 0))


"""
To use in game.py, add:
class Game:
    ...

Add to the initialization:
    self.background = Background('assets/background.gif')
    
And in the draw method:
    self.background.update()
    self.background.draw(self.screen)
"""