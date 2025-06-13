import pygame
from .constants import GRID_SIZE

class Ship:
    def render(self, screen, offset_x, offset_y, zoom_level=1.0):
        scaled_size = int(GRID_SIZE * zoom_level)
        rect = pygame.Rect(
            self.grid_position[0] * GRID_SIZE + offset_x,
            self.grid_position[1] * GRID_SIZE + offset_y,
            scaled_size,
            scaled_size
        )
        pygame.draw.rect(screen, self.color, rect) 