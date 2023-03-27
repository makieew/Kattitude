import pygame
import spritesheet as ss


class Button:
    def __init__(self, position, index, scale, w, h, path):
        self.sprite_sheet = ss.SpriteSheet(path)
        self.image = sprite_at(self.sprite_sheet, index, w, h, (255, 0, 255)).convert_alpha()
        width = self.image.get_width()
        height = self.image.get_height()
        s = scale
        self.image = pygame.transform.scale(self.image, (int(width * s), int(height * s)))
        self.rect = self.image.get_rect(topleft=position)
        self.clicked = False

    def draw(self, surface):

        position = pygame.mouse.get_pos()

        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return self.clicked


def sprite_at(image, index, w, h, background):
    img = image.image_at((0 + index * w, 0, w, h), background)
    return img
