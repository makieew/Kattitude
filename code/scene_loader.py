import pygame
import os
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


def load_images(path_to_directory):
    img_dict = {}
    for filename in os.listdir(path_to_directory):
        if filename.endswith('.png'):
            path = os.path.join(path_to_directory, filename)
            key = filename[:-4]
            img = pygame.image.load(path).convert()
            img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            img_dict[key] = img
    return img_dict
