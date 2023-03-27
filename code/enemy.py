import math
import spritesheet as ss
import pygame
from path import resource_path


class Enemy(pygame.sprite.Sprite):

    def __init__(self, position, surface):
        super().__init__()

        self.sprite_sheet = ss.SpriteSheet(resource_path("../graphics/enemy/dog.png"))
        self.img_w = 13
        self.img_h = 12
        self.scale = 5
        self.width = self.scale * self.img_w
        self.height = self.scale * self.img_h

        self.display_s = surface
        self.background = (255, 0, 255)
        self.animations = None
        self.set_animation_frames()
        self.frame_i = 0
        self.animation_speed = 0.1

        self.image = self.animations["move"]
        self.rect = pygame.Rect(self.image[0].get_rect(topleft=position))

        self.speed = 2
        self.direction = pygame.math.Vector2(0, 0)
        self.turned_right = True

        self.state = "move"

    def sprite_and_scale(self, index):
        img = self.sprite_sheet.image_at((0 + index * self.img_w, 0, self.img_w, self.img_h), self.background)
        return pygame.transform.scale(img, (self.width, self.height))

    def set_animation_frames(self):
        self.animations = {"move": [self.sprite_and_scale(0), self.sprite_and_scale(1),
                                    self.sprite_and_scale(2), self.sprite_and_scale(3)],
                           "bark": [self.sprite_and_scale(4), self.sprite_and_scale(5),
                                    self.sprite_and_scale(6), self.sprite_and_scale(7),
                                    self.sprite_and_scale(8), self.sprite_and_scale(9),
                                    self.sprite_and_scale(10), self.sprite_and_scale(11)]}

    def animate(self):
        animation = self.animations[self.state]

        self.frame_i += self.animation_speed
        if self.frame_i >= len(animation):
            self.frame_i = 0

        img = animation[int(self.frame_i)]
        if not self.turned_right:
            self.image = pygame.transform.flip(img, True, False)
        else:
            self.image = img

    # TO DO
    def check_state(self):
        if self.state == "bark":
            self.image = self.animations["bark"]
        else:
            self.image = self.animations["move"]

    def move(self):
        if self.state == "move":
            self.rect.x += self.speed

    def flip_image(self):
        if ((self.speed < 0 and self.turned_right) or (self.speed > 0 and not self.turned_right)) and self.state == "move":
            self.image = pygame.transform.flip(self.image, True, False)

    def turn(self):
        self.speed *= -1
        self.turned_right = not self.turned_right

    def perception(self, p_x, p_y):
        player_dist = math.sqrt((self.rect.x - p_x)**2 + (self.rect.y - p_y)**2)
        if 200 < player_dist <= 250:
            self.state = "bark"
            if self.rect.x < p_x and not self.turned_right:
                self.turned_right = True
            elif self.rect.x > p_x and self.turned_right:
                self.turned_right = False
        else:
            self.state = "move"

    def update(self):
        self.check_state()
        self.animate()
        self.move()
        self.flip_image()

