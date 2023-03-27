import spritesheet as ss
import pygame
import settings
from settings import meow, jump, cat
from datetime import datetime, timedelta
from path import resource_path


class Player(pygame.sprite.Sprite):

    def __init__(self, position, surface):
        super().__init__()

        # sprite dimensions
        self.sprite_sheet = ss.SpriteSheet(resource_path("../graphics/player/cat.png"))
        self.w_global = 16
        self.h_global = 11
        self.img_w = 12
        self.img_h = 11
        self.scale = 5
        self.width = self.scale * self.img_w
        self.height = self.scale * self.img_h

        # animations
        self.display_s = surface
        self.background = (255, 0, 255)
        self.animations = None
        self.set_animation_frames()
        self.frame_i = 0
        self.animation_speed = 0.1

        # status
        self.image = self.animations["idle"]
        self.mask = pygame.mask.from_surface(self.image[0])
        self.state = "idle"
        self.rect = pygame.Rect(self.image[0].get_rect(topleft=position))

        # physics
        self.speed = 4
        self.direction = pygame.math.Vector2(0, 0)
        self.g = 0.8
        self.jump_speed = -17
        self.collision_rect = pygame.Rect(self.rect.topleft, (58, 50))

        # rectangle adjustment
        self.grounded = False
        self.headboink = False
        self.left = False
        self.right = False
        self.turned_right = True

        # player health
        self.healthbars_ss = ss.SpriteSheet(resource_path("../graphics/player/healthbars.png"))     # 53,11
        self.healthbar = self.healthbars_ss.image_at((0, 0, 53, 11), self.background)
        self.healthbar = pygame.transform.scale(self.healthbar, (2 * 53, 2 * 11))
        self.health = 4
        self.health_index = 0
        self.invincible = datetime.now()
        self.dead = False

        # TO DO add audio here

    def sprite_and_scale(self, index, state):
        w = 0
        h = 0
        match state:
            case "idle":
                w = 12
                h = 11
            case "move":
                w = 14
                h = 11
            case "jump":
                w = 14
                h = 11
            case "fall":
                w = 14
                h = 11

        img = self.sprite_sheet.image_at((0 + index * self.w_global, 0, w, h), self.background)
        return pygame.transform.scale(img, (self.scale * w, self.scale * h))

    def set_animation_frames(self):
        self.animations = {"idle": [self.sprite_and_scale(0, "idle"), self.sprite_and_scale(1, "idle"), self.sprite_and_scale(2, "idle")],
                           "move": [self.sprite_and_scale(4, "move"), self.sprite_and_scale(5, "move"), self.sprite_and_scale(6, "move")],
                           "jump": [self.sprite_and_scale(4, "jump")],
                           "fall": [self.sprite_and_scale(4, "fall")]}

    def animate(self):
        animation = self.animations[self.state]

        self.frame_i += self.animation_speed
        if self.frame_i >= len(animation):
            self.frame_i = 0

        img = animation[int(self.frame_i)]
        self.mask = pygame.mask.from_surface(img)

        if self.turned_right:
            self.image = img
            self.rect.bottomleft = self.collision_rect.bottomleft

        else:
            self.image = pygame.transform.flip(img, True, False)
            self.rect.bottomright = self.collision_rect.bottomright

        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

        if not self.can_take_dmg():
            surf = self.mask.to_surface()
            surf.set_colorkey('black')
            if not self.turned_right:
                self.image = pygame.transform.flip(surf, True, False).convert_alpha()
            else:
                self.image = surf

    def get_state(self):
        if self.direction.x != 0:
            self.state = "move"
        elif self.direction.y < 0:
            self.state = "jump"
        elif self.direction.y > 0.8:
            self.state = "fall"
        else:
            self.state = "idle"

    def draw_health(self):
        self.healthbar = self.healthbars_ss.image_at((0 + self.health_index * 53, 0, 53, 11), self.background)
        self.healthbar = pygame.transform.scale(self.healthbar, (2 * 53, 2 * 11))
        self.display_s.blit(self.healthbar, (15, 15))

    def die(self):
        if self.health > 0:
            self.health = 0
            self.health_index = 4
        self.dead = True

    def can_take_dmg(self):
        return not (datetime.now() < self.invincible)

    def loose_health(self):
        if self.health > 0 and self.can_take_dmg():
            self.health -= 1
            self.health_index = 4 - self.health
            self.invincible = datetime.now() + timedelta(seconds=1)

        if self.health == 0:
            self.die()

    def input(self):
        keys_pressed = pygame.key.get_pressed()

        # RIGHT
        if keys_pressed[pygame.K_d]:
            self.direction.x = 1
            self.turned_right = True

        # LEFT
        elif keys_pressed[pygame.K_a]:
            self.direction.x = -1
            self.turned_right = False

        # Not moving
        else:
            self.direction.x = 0

        # JUMP
        if keys_pressed[pygame.K_w] and self.grounded:
            self.jump()

        # SPRINT
        if keys_pressed[pygame.K_LSHIFT] and self.grounded:
            self.direction.x = self.direction.x * self.speed / 2

        # MEOW
        if keys_pressed[pygame.K_m]:
            if not settings.muted and not cat.get_busy():
                cat.play(meow)

    def jump(self):
        if not settings.muted:
            pygame.mixer.Sound.play(jump)
        self.direction.y = self.jump_speed

    def gravity(self):
        self.direction.y += self.g
        self.collision_rect.y += self.direction.y

    def update(self):
        self.input()
        self.rect.x += self.direction.x * self.speed
        self.get_state()
        self.animate()

