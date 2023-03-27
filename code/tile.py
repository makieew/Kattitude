import pygame
from path import resource_path


class Tile(pygame.sprite.Sprite):

    def __init__(self, position, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=position)


class Constraint(Tile):
    def __init__(self, position, size):
        super().__init__(position, size)


class StaticTile(Tile):

    def __init__(self, position, size, surface):
        super().__init__(position, size)
        self.image = surface


class Water(StaticTile):
    def __init__(self, position, size, surface):
        super().__init__(position, size, surface)


class Sign(StaticTile):
    def __init__(self, position, size):
        super().__init__(position, size, pygame.image.load(resource_path("../graphics/terrain/sign.png")).convert_alpha())
        y_offset = position[1] + size
        self.rect = self.image.get_rect(bottomleft=(position[0], y_offset))


class Fish(StaticTile):
    def __init__(self, position, size, surface, value):
        super().__init__(position, size, surface)
        self.value = value


class Vase(Tile):
    def __init__(self, position, size, img):
        super().__init__(position, size)
        self.image = img
        self.x = position[0]
        self.y = position[1]
        self.direction = pygame.math.Vector2(0, 0)
        self.grounded = True
        self.t_falling = 0
        self.g = 0.6
        y_offset = position[1] + size
        self.rect = self.image.get_rect(bottomleft=(position[0], y_offset))

    def gravity(self):
        self.direction.y += self.g
        self.rect.y += self.direction.y

    def update_time(self):
        if not self.grounded:
            self.t_falling += 1
        else:
            self.t_falling = 0

    def update(self):
        self.rect.x += self.direction.x
