import pygame
import random

class Pipe:
    """
    Pipe object với top_rect và bottom_rect
    """
    def __init__(self, x, random_height, pipe_gap):
        # Bottom pipe
        self.bottom_rect = pygame.Rect(0, 0, 52, 320)
        self.bottom_rect.midtop = (x, random_height)

        # Top pipe
        self.top_rect = pygame.Rect(0, 0, 52, 320)
        self.top_rect.midbottom = (x, random_height - pipe_gap)

        # Movement (chỉ level 2 di chuyển lên xuống)
        self.movement = 0

    def move(self, level):
        # Di chuyển sang trái
        self.bottom_rect.centerx -= 4
        self.top_rect.centerx -= 4

        # Level 2: di chuyển lên xuống
        if level == 2:
            self.bottom_rect.centery += self.movement
            self.top_rect.centery += self.movement
            if self.bottom_rect.centery < 150 or self.bottom_rect.centery > 550:
                self.movement *= -1

    def is_off_screen(self):
        return self.bottom_rect.right < -50

    def get_rects(self):
        return [self.top_rect, self.bottom_rect]
