from config.settings.settings import *
import pygame
from .pawn import Pawn

class UserEvent:
    def __init__(self):
        self._init_mouse_indicators()
        self.possible_moves = []
    
    def _init_mouse_indicators(self):
        """Initialize mouse-related visual indicators"""
        self.mypos = pygame.mouse.get_pos()
        # Mouse rectangle indicator
        self.mouse_rect = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.mouse_rect.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mouse_rect, COLOR['GREEN'], self.mouse_rect.get_rect(), 2)
        # Possible moves indicator
        self.possible_moves_surface = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.possible_moves_surface.fill((0, 255, 0, 100))

    def handleEvent(self, objects, event, deletedsprites, chessboard):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_left_click(event, objects, chessboard)
            elif event.button == 3:
                return self._handle_right_click(event, objects, deletedsprites)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            return self._handle_piece_movement(objects, chessboard)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_drag_motion(event, objects)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self._handle_piece_restore(objects, deletedsprites)
        return False

    def _handle_left_click(self, event, objects, chessboard):
        """Handle left mouse button click"""
        for obj in objects:
            if obj.checkCollision(event.pos) and obj.side == 0:
                obj.selected = True
                self.possible_moves = obj.get_possible_moves(chessboard)
        return False

    def _handle_right_click(self, event, objects, deletedsprites):
        """Handle right mouse button click"""
        for obj in objects:
            if obj.rect.collidepoint(event.pos):
                objects.remove(obj)
                deletedsprites.append(obj)
                break
        return False

    def _handle_piece_movement(self, objects, chessboard):
        """Handle piece movement when mouse button is released"""
        moved = False
        for obj in objects:
            if obj.selected:
                obj.snapToGrid()
                current_pos = (obj.rect.x // TILESIZE, obj.rect.y // TILESIZE)
                old_pos = (obj.last_position[0] // TILESIZE, obj.last_position[1] // TILESIZE)
                
                if current_pos in self.possible_moves:
                    moved = self._execute_move(obj, current_pos, old_pos, objects, chessboard)
                else:
                    self._reset_move(obj, old_pos, chessboard)
                
                obj.selected = False
                self.possible_moves = []
        return moved

    def _execute_move(self, piece, current_pos, old_pos, objects, chessboard):
        """Execute a valid piece movement"""
        grid_x, grid_y = current_pos
        old_grid_x, old_grid_y = old_pos

        target_piece = chessboard.map[grid_y][grid_x]
        if target_piece is not None and target_piece.side != piece.side:
            objects.remove(target_piece)
            target_piece.is_captured = True

        chessboard.map[old_grid_y][old_grid_x] = None
        chessboard.map[grid_y][grid_x] = piece

        if isinstance(piece, Pawn):
            piece.move(grid_x, grid_y)
        else:
            piece.last_position = (piece.rect.x, piece.rect.y)
            piece.pos = (grid_x, grid_y)
        return True

    def _reset_move(self, piece, old_pos, chessboard):
        """Reset piece to its original position"""
        old_grid_x, old_grid_y = old_pos
        piece.reset_to_last_position()
        chessboard.map[old_grid_y][old_grid_x] = piece

    def _handle_drag_motion(self, event, objects):
        """Handle piece dragging motion"""
        for obj in objects:
            if obj.selected:
                obj.update(event.pos)

    def _handle_piece_restore(self, objects, deletedsprites):
        """Handle piece restoration with 'R' key"""
        if deletedsprites:
            objects.append(deletedsprites.pop())

    def draw(self, screen):
        self.mypos = pygame.mouse.get_pos()
        if self.mypos[0] < 750 and self.mypos[1] < 750:
            screen.blit(self.mouse_rect, (self.mypos[0] - 50, self.mypos[1] - 50))
        for move in self.possible_moves:
            x, y = move
            screen.blit(self.possible_moves_surface, (x * TILESIZE, y * TILESIZE))