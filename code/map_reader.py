import pygame
from csv import reader


def import_csv(path):
    terrain = []
    with open(path) as l_map:
        level = reader(l_map, delimiter=',')
        for row in level:
            terrain.append(list(row))

        return terrain


def import_graphics(path, width, height):
    tiles = []
    img = pygame.image.load(path).convert_alpha()
    tile_x = int(img.get_size()[0] / width)
    tile_y = int(img.get_size()[1] / height)

    for row in range(tile_y):
        for col in range(tile_x):
            pos = (col * width, row * height)
            surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            surface.blit(img, (0, 0), pygame.Rect(pos[0], pos[1], width, height))
            tiles.append(surface)

    return tiles
