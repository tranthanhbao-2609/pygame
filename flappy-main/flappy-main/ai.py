import pygame
from typing import List
from pipe import Pipe  # import Pipe từ pipe.py

class AIPlayer:
    """
    AI Player thông minh tự động chơi Flappy Bird
    """
    def __init__(self, x_pos: int = 250, y_pos: int = 384, pipe_gap: int = 180):
        self.bird_rect = pygame.Rect(x_pos - 17, y_pos - 12, 34, 24)
        self.bird_rect.center = (x_pos, y_pos)

        self.bird_movement = 0.0
        self.alive = True
        self.score = 0
        self.pipe_gap = pipe_gap

        self.last_decision_time = 0
        self.decision_interval = 100  # AI quyết định mỗi 100ms

    def should_jump(self, pipe_list: List[Pipe], current_time: int) -> bool:
        if not self.alive:
            return False
        if current_time - self.last_decision_time < self.decision_interval:
            return False
        self.last_decision_time = current_time

        if not pipe_list:
            return self.bird_rect.centery > 400

        # Tìm pipe gần nhất phía trước
        closest_pipe = None
        min_distance = float('inf')
        for pipe in pipe_list:
            if pipe.bottom_rect.centerx > self.bird_rect.centerx:
                distance = pipe.bottom_rect.centerx - self.bird_rect.centerx
                if distance < min_distance:
                    min_distance = distance
                    closest_pipe = pipe

        if closest_pipe:
            gap_center = (closest_pipe.top_rect.bottom + closest_pipe.bottom_rect.top) / 2
            if self.bird_rect.centery > gap_center + 20:
                return True

        return False

    def jump(self):
        if self.alive:
            self.bird_movement = -8

    def update_movement(self, gravity: float):
        if not self.alive:
            return
        self.bird_movement += gravity
        self.bird_rect.centery += self.bird_movement

    def check_collision(self, pipe_list: List[Pipe]) -> bool:
        if not self.alive:
            return False
        for pipe in pipe_list:
            if self.bird_rect.colliderect(pipe.top_rect) or self.bird_rect.colliderect(pipe.bottom_rect):
                self.alive = False
                return False
        if self.bird_rect.top <= -75 or self.bird_rect.bottom >= 650:
            self.alive = False
            return False
        return True

    def increment_score(self):
        if self.alive:
            self.score += 1

    def reset(self, x: int, y: int):
        self.bird_rect.center = (x, y)
        self.bird_movement = 0.0
        self.alive = True
        self.score = 0
        self.last_decision_time = 0

    def get_status(self) -> dict:
        return {
            'alive': self.alive,
            'score': self.score,
            'position': (self.bird_rect.centerx, self.bird_rect.centery),
            'velocity': self.bird_movement
        }

    def __str__(self):
        status = "ALIVE" if self.alive else "DEAD"
        return f"AI Player - Score: {self.score} | Status: {status} | Pos: ({self.bird_rect.centerx}, {self.bird_rect.centery})"
