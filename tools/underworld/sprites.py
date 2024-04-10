# sprites.py

import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, x, y):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
