import pygame

class Text:
    def __init__(self, text, font_size, color, position):
        self.font = pygame.font.SysFont("04b30", font_size)
        self.text = text
        self.color = color
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect(topleft=position)

    def update(self, new_text=None):
        if new_text:
            self.text = new_text
            self.rendered_text = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.rendered_text, self.rect)
