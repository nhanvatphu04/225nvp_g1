from config.settings.settings import *
import pygame
from .pawn import Pawn

class UserEvent:
    def __init__(self):
        self.mypos = pygame.mouse.get_pos()
        self.mouse_rect = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.mouse_rect.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mouse_rect, COLOR['GREEN'], self.mouse_rect.get_rect(), 2)
        self.possible_moves_surface = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.possible_moves_surface.fill((0, 255, 0, 100))
        self.possible_moves = []

    def handleEvent(self, objects, event, deletedsprites, chessboard):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for obj in objects:
                if obj.checkCollision(mouse_pos) and obj.side == 0:
                    obj.selected = True
                    self.possible_moves = obj.get_possible_moves(chessboard)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            moved = False
            for obj in objects:
                if obj.selected:
                    obj.snapToGrid()
                    grid_x = obj.rect.x // TILESIZE
                    grid_y = obj.rect.y // TILESIZE
                    old_x, old_y = obj.last_position
                    old_grid_x = old_x // TILESIZE
                    old_grid_y = old_y // TILESIZE
                    
                    if (grid_x, grid_y) in self.possible_moves:
                        target_piece = chessboard.map[grid_y][grid_x]
                        if target_piece is not None:
                            if target_piece.side != obj.side:
                                objects.remove(target_piece)
                                target_piece.is_captured = True
                    
                        if isinstance(obj, Pawn):
                            chessboard.map[old_grid_y][old_grid_x] = None
                            chessboard.map[grid_y][grid_x] = obj
                            obj.move(grid_x, grid_y)
                        else:
                            chessboard.map[old_grid_y][old_grid_x] = None
                            chessboard.map[grid_y][grid_x] = obj
                            obj.last_position = (obj.rect.x, obj.rect.y)
                            obj.pos = (grid_x, grid_y)
                        moved = True
                    else:
                        obj.reset_to_last_position()
                        chessboard.map[old_grid_y][old_grid_x] = obj
                    
                    obj.selected = False
                    self.possible_moves = []
            return moved

        elif event.type == pygame.MOUSEMOTION:
            for obj in objects:
                if obj.selected:
                    obj.update(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouse_pos = event.pos
            for obj in objects:
                if obj.rect.collidepoint(mouse_pos):
                    objects.remove(obj)
                    deletedsprites.append(obj)
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and deletedsprites:
                objects.append(deletedsprites.pop())
        return False

    def draw(self, screen):
        self.mypos = pygame.mouse.get_pos()
        if self.mypos[0] < 750 and self.mypos[1] < 750:
            screen.blit(self.mouse_rect, (self.mypos[0] - 50, self.mypos[1] - 50))
        for move in self.possible_moves:
            x, y = move
            screen.blit(self.possible_moves_surface, (x * TILESIZE, y * TILESIZE))