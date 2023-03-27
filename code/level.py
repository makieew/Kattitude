import pygame
from settings import WINDOW_HEIGHT, TILE_SIZE, FONT, CAMERA_BORDERS
from map_reader import import_csv, import_graphics
from tile import StaticTile, Sign, Vase, Fish, Constraint, Tile, Water
from player import Player
from enemy import Enemy
from path import resource_path


class Level:

    def __init__(self, level_data, surface):
        self.display_s = surface
        self.scene_shift_x = 0
        self.scene_shift_y = 0
        self.collision_x = 0

        # TEST - Camera
        self.all_sprites = CameraGroup(self.display_s)

        # csv
        # player
        player_layout = import_csv(level_data["player"])
        self.player = pygame.sprite.GroupSingle()
        self.ending = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # dog
        dog_layout = import_csv(level_data["dog"])
        self.constraints = pygame.sprite.Group()
        self.dogs = self.setup(dog_layout, "dog")

        # terrain
        terrain_layout = import_csv(level_data["terrain"])
        self.terrain_sprites = self.setup(terrain_layout, "terrain")

        # water
        water_layout = import_csv(level_data["water"])
        self.water_sprites = self.setup(water_layout, "water")

        # sign
        sign_layout = import_csv(level_data["sign"])
        self.sign_sprites = self.setup(sign_layout, "sign")

        # fish
        fish_layout = import_csv(level_data["fish"])
        self.fish_sprites = self.setup(fish_layout, "fish")

        # score elements
        self.vase_element = pygame.image.load(resource_path("../graphics/objects/vase.png"))
        self.vase_element = pygame.transform.scale(self.vase_element, (12, 20))
        self.vases_destroyed = 0
        self.total_vases = 0

        self.fish_element = pygame.image.load(resource_path("../graphics/objects/one_fish.png"))
        self.fish_element = pygame.transform.scale(self.fish_element, (20, 16))
        self.fish_score = 0

        # vases
        vases_layout = import_csv(level_data["vases"])
        self.vase_sprites = self.setup(vases_layout, "vases")

        self.all_sprites.add(self.player, self.ending, self.constraints, self.dogs, self.terrain_sprites, self.water_sprites, self.sign_sprites, self.fish_sprites, self.vase_sprites)

    def player_setup(self, layout_map):
        for i, row in enumerate(layout_map):
            for j, val in enumerate(row):
                # start
                if val == "0":
                    pos = (j * TILE_SIZE, i * TILE_SIZE - 500)
                    sprite = Player(pos, self.display_s)
                    self.player.add(sprite)
                # end
                elif val == "1":
                    pos = (j * TILE_SIZE, i * TILE_SIZE - WINDOW_HEIGHT)
                    self.ending.add(Tile(pos, TILE_SIZE))

    def setup(self, layout_map, tile_type):
        sprite_group = pygame.sprite.Group()
        sprite = None

        for i, row in enumerate(layout_map):
            for j, val in enumerate(row):
                if val != "-1":
                    pos = (j * TILE_SIZE, i * TILE_SIZE - WINDOW_HEIGHT)
                    match tile_type:
                        case "terrain":
                            terrain_tiles = import_graphics(resource_path("../graphics/terrain/terrain_tiles.png"), 50, 50)
                            tile_surface = terrain_tiles[int(val)]
                            sprite = StaticTile(pos, TILE_SIZE, tile_surface)

                        case "water":
                            water_tiles = import_graphics(resource_path("../graphics/terrain/water.png"), 50, 50)
                            tile_surface = water_tiles[int(val)]
                            sprite = Water(pos, TILE_SIZE, tile_surface)

                        case "dog":
                            # constraint
                            if val == '0':
                                self.constraints.add(Constraint(pos, TILE_SIZE))
                            # spawn enemy
                            elif val == '1':
                                pos = (j * TILE_SIZE, i * TILE_SIZE - WINDOW_HEIGHT - 10)
                                sprite = Enemy(pos, self.display_s)

                        case "sign":
                            sprite = Sign(pos, TILE_SIZE)

                        case "fish":
                            fish_tiles = import_graphics(resource_path("../graphics/objects/fish.png"), 50, 50)
                            tile_surface = fish_tiles[int(val)]
                            if val == '0':
                                sprite = Fish(pos, TILE_SIZE, tile_surface, 50)
                            elif val == '1':
                                sprite = Fish(pos, TILE_SIZE, tile_surface, 10)

                        case "vases":
                            # 24 x 40
                            vase_tiles = import_graphics(resource_path("../graphics/objects/vases.png"), 24, 40)
                            tile_surface = vase_tiles[int(val)]
                            if val == '0':
                                sprite = Vase(pos, TILE_SIZE, tile_surface)
                                self.total_vases += 1
                            elif val == '1':
                                sprite = Vase(pos, TILE_SIZE, tile_surface)
                                self.total_vases += 1
                            elif val == '2':
                                sprite = Vase(pos, TILE_SIZE, tile_surface)
                                self.total_vases += 1

                    if sprite:
                        sprite_group.add(sprite)

        return sprite_group

    def vertical_collision(self):
        player = self.player.sprite
        player.gravity()

        collided_objects = self.terrain_sprites.sprites() + self.vase_sprites.sprites()

        for sprite in collided_objects:
            if sprite.rect.colliderect(player.collision_rect):
                # player top collision
                if player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.headboink = True

                # player bottom collision
                elif player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.grounded = True

        if player.grounded and player.direction.y < 0 or player.direction.y > 1:
            player.grounded = False

    def horizontal_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        # fix + self.vase_sprites.sprites()
        for sprite in self.terrain_sprites.sprites() + self.vase_sprites.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                # right collision
                if player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.right = True
                    self.collision_x = player.rect.right
                    # vase move right
                    if type(sprite) == Vase:
                        sprite.direction.x = 1

                # left collision
                elif player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.left = True
                    self.collision_x = player.rect.left
                    # vase move left
                    if type(sprite) == Vase:
                        sprite.direction.x = -1

            else:
                if type(sprite) == Vase:
                    sprite.direction.x = 0

    def vase_physics(self):
        for vase in self.vase_sprites.sprites():
            vase.gravity()
            for ground in self.terrain_sprites.sprites():
                if ground.rect.colliderect(vase.rect):
                    if vase.direction.y > 0:
                        vase.rect.bottom = ground.rect.top
                        vase.direction.y = 0
                        vase.grounded = True

            if vase.grounded and vase.direction.y > 1 or vase.direction.y < 0:
                vase.grounded = False

            vase.update_time()
            if vase.t_falling > 30 and not vase.grounded:
                vase.kill()
                self.vases_destroyed += 1

    def dog_collision(self):
        # dog & constraints
        for dog in self.dogs.sprites():
            if pygame.sprite.spritecollide(dog, self.constraints, False):
                dog.turn()

        # dog & player
        collided = pygame.sprite.spritecollide(self.player.sprite, self.dogs, False)
        if collided:
            self.player.sprite.loose_health()

    def dog_ai(self):
        player = self.player.sprite
        for dog in self.dogs.sprites():
            dog.perception(player.rect.x, player.rect.y)

    def fish_collision(self):
        collided = pygame.sprite.spritecollide(self.player.sprite, self.fish_sprites, True)
        if collided:
            for fish in collided:
                self.fish_score += fish.value

    def water_collision(self):
        collided = pygame.sprite.spritecollide(self.player.sprite, self.water_sprites, False)
        if collided:
            self.player.sprite.die()

    def update_score(self):
        self.display_s.blit(self.fish_element, (200, 20))
        fish = FONT.render("x " + str(self.fish_score), True, (0, 0, 0))
        text_rect1 = fish.get_rect(topleft=(225, 15))
        self.display_s.blit(fish, text_rect1)

    def update_vase_count(self):
        self.display_s.blit(self.vase_element, (140, 15))
        vases = FONT.render(str(self.vases_destroyed) + "/" + str(self.total_vases), True, (0, 0, 0))
        text_rect1 = vases.get_rect(topleft=(160, 15))
        self.display_s.blit(vases, text_rect1)

    def check_level_ending(self):
        player = self.player.sprite
        if pygame.sprite.spritecollide(player, self.ending, False):
            if self.total_vases - self.vases_destroyed == 0:
                return True
        return False

    def get_level_score(self):
        return self.fish_score

    def check_player_health(self):
        return self.player.sprite.dead

    def run(self):
        self.player.update()
        self.dogs.update()
        self.vase_sprites.update()

        self.horizontal_collision()
        self.vertical_collision()
        self.water_collision()

        self.vase_physics()
        self.fish_collision()
        self.dog_collision()
        self.dog_ai()

        self.all_sprites.custom_draw(self.player.sprite)

        self.update_vase_count()
        self.update_score()
        self.player.sprite.draw_health()


class CameraGroup(pygame.sprite.Group):
    def __init__(self, display):
        super().__init__()
        self.display_s = display
        self.offset = pygame.math.Vector2(100, 300)

        # camera
        cam_left = CAMERA_BORDERS['left']
        cam_top = CAMERA_BORDERS['top']
        cam_width = self.display_s.get_size()[0] - (cam_left + CAMERA_BORDERS['right'])
        cam_height = self.display_s.get_size()[1] - (cam_top + CAMERA_BORDERS['bottom'])

        self.camera_rect = pygame.Rect(cam_left, cam_top, cam_width, cam_height)

    def custom_draw(self, player):

        # getting the camera position
        if player.rect.left < self.camera_rect.left:
            self.camera_rect.left = player.rect.left

        if player.rect.right > self.camera_rect.right:
            self.camera_rect.right = player.rect.right

        if player.rect.top < self.camera_rect.top:
            self.camera_rect.top = player.rect.top

        if player.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = player.rect.bottom

        # camera offset
        self.offset = pygame.math.Vector2(
                self.camera_rect.left - CAMERA_BORDERS['left'],
                self.camera_rect.top - CAMERA_BORDERS['top'])

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            if type(sprite) == Constraint or type(sprite) == Tile:
                sprite.update(offset_pos)
            else:
                self.display_s.blit(sprite.image, offset_pos)
