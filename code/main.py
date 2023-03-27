import pygame.display
import settings
from settings import *
from level import Level
from data import *
import menu_elements
import pickle
import os
import scene_loader
from path import resource_path
import sys


pygame.init()

# resolution
display_info = pygame.display.Info()
w = display_info.current_w
h = display_info.current_h

flags = 0
if w > 1920 and h > 1080:
    flags = pygame.SCALED

WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=flags)

pygame.display.set_caption("Kattitude")

clock = pygame.time.Clock()
FPS = 60

# level
level_index = 0
level = level_1
current_level = Level(level_1, WIN)
levels = [level_1, level_2, level_3]

# scenes
intro_dict = scene_loader.load_images(resource_path("../graphics/intro"))
outro_dict = scene_loader.load_images(resource_path("../graphics/outro"))

# fonts
pygame.font.init()
FONT = pygame.font.Font(resource_path('NotoSans-Bold.ttf'), 12)
FONTGO = pygame.font.Font(resource_path('NotoSans-Bold.ttf'), 48)

# menu variables
run = True
paused = True
game_state = ""
in_game_pause = False

# menu buttons
play_button = menu_elements.Button((WIN.get_width() * 0.5 - 35 / 2 * 5, WIN.get_height() * 0.2), 0, 5, 35, 15, resource_path("../graphics/menu/buttons.png"))
quit_button = menu_elements.Button((WIN.get_width() * 0.5 - 35 / 2 * 5, WIN.get_height() * 0.6), 1, 5, 35, 15, resource_path("../graphics/menu/buttons.png"))
resume_button = menu_elements.Button((WIN.get_width() * 0.5 - 35 / 2 * 5, WIN.get_height() * 0.2), 2, 5, 35, 15, resource_path("../graphics/menu/buttons.png"))
reset_button = menu_elements.Button((WIN.get_width() * 0.5 - 35 / 2 * 5, WIN.get_height() * 0.4), 3, 5, 35, 15, resource_path("../graphics/menu/buttons.png"))

# control buttons
mute_button = menu_elements.Button((WIN.get_width() * 0.966 - 20 / 2 * 2, WIN.get_height() * 0.02), 0, 2, 20, 20, resource_path("../graphics/menu/controls.png"))
unmute_button = menu_elements.Button((WIN.get_width() * 0.966 - 20 / 2 * 2, WIN.get_height() * 0.02), 1, 2, 20, 20, resource_path("../graphics/menu/controls.png"))

# load settings
if os.path.isfile(resource_path("save.pickle")):
    save = open("save.pickle", "rb")
    settings.saved_settings = pickle.load(save)
    settings.muted = settings.saved_settings["muted"]

# music
pygame.mixer.music.load(resource_path("../audio/bck_music.mp3"))
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)
if settings.muted:
    pygame.mixer.music.pause()

# score
total_score = 0
high_score = 0

if os.path.isfile(resource_path("score.pickle")):
    score = open("score.pickle", "rb")
    settings.score_settings = pickle.load(score)
    high_score = settings.score_settings["score"]


def main_menu():
    global game_state, paused, run

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                run = False
                main()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and game_state == "playing":
                    paused = False

        WIN.fill((204, 204, 255))

        if game_state == "":
            if play_button.draw(WIN):
                game_state = "playing"
                paused = False
                play_intro()
        else:
            if resume_button.draw(WIN):
                paused = False

            if reset_button.draw(WIN):
                paused = False
                game_state = "reset"

        if quit_button.draw(WIN):
            run = False
            paused = False

        pygame.display.update()

    main()


def play_intro():
    global paused, run, intro_dict, game_state

    play = True
    s_index = 1
    scene = intro_dict["s1"]

    while play:
        WIN.fill(0)
        WIN.blit(scene, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                run = False
                main()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    s_index += 1
                    if s_index > len(intro_dict):
                        main()
                    else:
                        scene = intro_dict["s" + str(s_index)]


def play_outro():
    global paused, run, outro_dict

    play = True
    run = False
    s_index = 1
    scene = outro_dict["s1"]

    while play:
        WIN.fill(0)
        WIN.blit(scene, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                play = False
                run = False
                main()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    s_index += 1
                    if s_index > len(outro_dict):
                        play = False
                        play_ending_menu()
                    else:
                        scene = outro_dict["s" + str(s_index)]


def play_ending_menu():
    global run, paused
    paused = True

    while paused:
        WIN.fill((204, 204, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                run = False
                main()

        if quit_button.draw(WIN):
            run = False
            paused = False

        txt = FONTGO.render("Thank you for playing!", True, (88, 72, 128))
        text_rect = txt.get_rect()
        text_rect.center = (470, 140)
        WIN.blit(txt, text_rect)

        s = FONTS.render("score: " + str(total_score) + "  |  highest score: " + str(high_score), True, (88, 72, 128))
        text_rect2 = s.get_rect()
        text_rect2.center = (470, 250)
        WIN.blit(s, text_rect2)

        dev = FONTS.render("developed by Marta Rašeta", True, (88, 72, 128))
        text_rect3 = dev.get_rect()
        text_rect3.center = (570, 190)
        WIN.blit(dev, text_rect3)

        pygame.display.update()

    main()


def change_level():
    global level_index, current_level, level, total_score

    total_score += current_level.get_level_score()

    if level_index != 2:
        level_index += 1
        level = levels[level_index]
        current_level = Level(level, WIN)

    else:
        play_outro()


def check_new_highscore():
    global high_score, total_score
    if total_score > high_score:
        high_score = total_score
    return high_score


def game_over_screen():
    global game_state, paused, run, high_score

    game_over_screen_fade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    game_over_screen_fade.fill((0, 0, 0))
    game_over_screen_fade.set_alpha(150)
    WIN.blit(game_over_screen_fade, (0, 0))

    high_score = check_new_highscore()

    while paused:
        go = FONTGO.render("GAME OVER", True, (255, 255, 255))
        text_rect = go.get_rect()
        text_rect.center = (450, 100)
        WIN.blit(go, text_rect)

        s = FONTS.render("score: " + str(total_score) + "  |  highest score: " + str(high_score), True, (255, 255, 255))
        text_rect2 = go.get_rect()
        text_rect2.center = (470, 165)
        WIN.blit(s, text_rect2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                run = False
                main()

        if reset_button.draw(WIN):
            paused = False
            game_state = "reset"

        if quit_button.draw(WIN):
            run = False
            paused = False

        pygame.display.update()

    main()


def main():
    global paused, run, current_level, level, game_state, total_score
    while run:
        click = False

        if current_level.check_player_health() and game_state != "reset":
            game_state = "game_over"
            paused = True
            game_over_screen()

        elif paused:
            main_menu()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or game_state == "quit":
                    run = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True

            WIN.fill((204, 204, 255))

            if game_state == "reset":
                current_level = Level(level, WIN)
                game_state = "playing"

            current_level.run()
            if current_level.check_level_ending():
                change_level()

            if settings.muted:
                if unmute_button.draw(WIN) and click:
                    settings.muted = False
                    pygame.mixer.music.unpause()
                    pygame.mixer.unpause()
                    settings.saved_settings["muted"] = False

            else:
                if mute_button.draw(WIN) and click:
                    settings.muted = True
                    pygame.mixer.music.pause()
                    pygame.mixer.pause()
                    settings.saved_settings["muted"] = True

            pygame.display.update()
            clock.tick(60)

    save_out = open("save.pickle", "wb")
    pickle.dump(settings.saved_settings, save_out)
    save_out.close()

    settings.score_settings["score"] = high_score
    score_out = open("score.pickle", "wb")
    pickle.dump(settings.score_settings, score_out)
    score_out.close()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
