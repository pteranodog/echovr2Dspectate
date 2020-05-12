#!/usr/bin/env python3
import json
import pygame
import sys
from pygame.locals import *
import requests

# config file
try:
    with open("config.json", "r") as configfile:
        config = json.load(configfile)
    # general config
    IP = config["ip_address"]
    OVERRIDE_IP = config["override_ip_with_full_path"]
    FULL_PATH = config["full_path"]
    ORANGE_TEAM_NAME = config["orange_team_name"]
    BLUE_TEAM_NAME = config["blue_team_name"]
    USE_RED = config["use_red_for_orange_team"]
    # sizes
    DIMS_SCALE = config["sizes"]["pixels_per_meter"]
    PLAYER_SCALE = config["sizes"]["player_size"]
    DISC_SCALE = config["sizes"]["disc_size"]
    FONT_SIZE = config["sizes"]["font_size"]
    LINE_THICKNESS = config["sizes"]["line_thickness_if_no_background"]
    # elements
    SHOW_TIME = config["elements"]["show_time"]
    SHOW_NAMES = config["elements"]["show_names"]
    SHOW_SCORES = config["elements"]["show_scores"]
    SHOW_HEIGHT = config["elements"]["show_height_with_color"]
    SHOW_POSSESSION = config["elements"]["show_possession"]
    PURPLE_HOST = config["elements"]["show_host_as_purple"]
    # colors
    BLACK = config["colors"]["black"]
    WHITE = config["colors"]["white"]
    RED = config["colors"]["red"]
    GREEN = config["colors"]["green"]
    BLUE = config["colors"]["blue"]
    ORANGE = config["colors"]["orange"]
    PURPLE = config["colors"]["purple"]
    TIMER_COLOR = config["colors"]["timer_color"]
    POINTS_COLOR = config["colors"]["points_color"]
    NAMES_COLOR = config["colors"]["names_color"]
    # stuns
    FLASH_WHEN_STUNNED = config["stuns"]["flash_when_stunned"]
    STUN_COUNTER_RESET = config["stuns"]["stun_flash_speed"]
    # background options
    USE_BG_IMG = config["background_image"]["use_background_image"]
    BG_IMG_FILE = config["background_image"]["image_file"]
    BG_OFFSET = config["background_image"]["offset_xy"]
except FileNotFoundError:
    print("No config file found. Try downloading the config file again.")
    input()
    sys.exit()
except KeyError:
    print("Error in config file. Try downloading the config file again.")
    input()
    sys.exit()

# other globals
DIMS_ARENA = (30, 20, 80)
G_DIST = DIMS_SCALE * 4
DIMS = (DIMS_ARENA[2] * DIMS_SCALE, DIMS_ARENA[0] * DIMS_SCALE)
SURFACE = None
FONT = None
STUN_COUNTER = 0


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


if USE_BG_IMG:
    BG = Background(BG_IMG_FILE, BG_OFFSET)


def draw_text(position, text, text_color):
    text = FONT.render(text, True, text_color, None)
    text_rect = text.get_rect()
    text_rect.centerx = position[0]
    text_rect.centery = position[1]
    SURFACE.blit(text, text_rect)


def refresh():
    SURFACE.fill(BLACK)
    if USE_BG_IMG:
        SURFACE.blit(BG.image, BG.rect)
    else:
        pygame.draw.line(SURFACE, WHITE, (10, 10), (DIMS[0] - 10, 10), LINE_THICKNESS)
        pygame.draw.line(SURFACE, WHITE, (10, 10), (10, DIMS[1] - 10), LINE_THICKNESS)
        pygame.draw.line(
            SURFACE, WHITE, (10, DIMS[1] - 10), (DIMS[0] - 10, DIMS[1] - 10), LINE_THICKNESS
        )
        pygame.draw.line(
            SURFACE, WHITE, (DIMS[0] - 10, 10), (DIMS[0] - 10, DIMS[1] - 10), LINE_THICKNESS
        )
        g1 = (
            (G_DIST, SURFACE.get_rect().centery - 15),
            (G_DIST, SURFACE.get_rect().centery + 15)
        )
        g2 = (
            (DIMS[0] - G_DIST, SURFACE.get_rect().centery - 15),
            (DIMS[0] - G_DIST, SURFACE.get_rect().centery + 15),
        )
        pygame.draw.line(SURFACE, BLUE, g1[0], g1[1], LINE_THICKNESS)
        pygame.draw.line(SURFACE, RED, g2[0], g2[1], LINE_THICKNESS)
        pygame.draw.line(
            SURFACE, BLUE, (SURFACE.get_rect().centerx - (4 * DIMS_SCALE), 10),
            (SURFACE.get_rect().centerx - (4 * DIMS_SCALE), DIMS[1]-10), LINE_THICKNESS)
        pygame.draw.line(
            SURFACE, RED, (SURFACE.get_rect().centerx + (4 * DIMS_SCALE), 10),
            (SURFACE.get_rect().centerx + (4 * DIMS_SCALE), DIMS[1] - 10), LINE_THICKNESS)


def coord_transform(position):
    x = (position[0] + (DIMS_ARENA[0] / 2)) * DIMS_SCALE
#   y is unused
#   y = (position[1] + (DIMS_ARENA[1] / 2)) * DIMS_SCALE
    z = (position[2] + (DIMS_ARENA[2] / 2)) * DIMS_SCALE

    return int(z), int(x)


def draw_player(player, team_color):
    if player["stunned"] and (STUN_COUNTER < (STUN_COUNTER_RESET / 2)) and FLASH_WHEN_STUNNED:
        return True
    position = coord_transform(player["position"])
    if player["possession"] and SHOW_POSSESSION:
        pygame.draw.circle(SURFACE, GREEN, position, int(12*PLAYER_SCALE), 0)
    pygame.draw.circle(SURFACE, team_color, position, int(10*PLAYER_SCALE), 0)
    if SHOW_HEIGHT:
        y_color_num = 255 * ((player["position"][1] + 10) / 20)
        height_color = (y_color_num, y_color_num, y_color_num)
        pygame.draw.circle(SURFACE, height_color, position, int(7*PLAYER_SCALE), 0)
    if SHOW_NAMES:
        position2 = (position[0], position[1] - ((int(12*PLAYER_SCALE))+(FONT_SIZE/2)))
        draw_text(position2, player["name"], NAMES_COLOR)


def draw_disc(disc):
    pos = disc["position"]
    position = coord_transform(pos)
    pygame.draw.circle(SURFACE, WHITE, position, int(7*DISC_SCALE), 0)
    if SHOW_HEIGHT:
        y_color_num = 255 * ((disc["position"][1] + 10) / 20)
        height_color = (y_color_num, y_color_num, y_color_num)
        pygame.draw.circle(SURFACE, height_color, position, int(5*DISC_SCALE), 0)


def get_frame():
    try:
        content = json.loads(requests.get(FULL_PATH if OVERRIDE_IP else ("http://"+IP+"/session")).content)
        return content
    except requests.exceptions.ConnectionError:
        print("Could not find an EchoVR session at {}.".format(IP))
        input()
        sys.exit()


def draw_frame(frame_data):
    for team in frame_data["teams"]:
        team_color = (RED if USE_RED else ORANGE) if ORANGE_TEAM_NAME in team["team"] else BLUE
        for player in team["players"]:
            if (player["name"] == frame_data["client_name"]) and PURPLE_HOST:
                team_color = PURPLE
            draw_player(player, team_color)
    draw_disc(frame_data["disc"])
    if SHOW_TIME:
        draw_text((SURFACE.get_rect().centerx, 20), frame_data["game_clock_display"], TIMER_COLOR)
    if SHOW_SCORES:
        draw_text((20, 20), str(frame_data["teams"][0]["stats"]["points"]), POINTS_COLOR)
        draw_text((DIMS[0] - 20, 20), str(frame_data["teams"][1]["stats"]["points"]), POINTS_COLOR)


if __name__ == "__main__":
    pygame.init()

    SURFACE = pygame.display.set_mode(DIMS, 0, 32)
    FONT = pygame.font.SysFont(None, FONT_SIZE)
    pygame.display.set_caption("Echo VR Spectator")

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        try:
            frame = get_frame()
            refresh()
            draw_frame(frame)
            pygame.display.update()
        except json.decoder.JSONDecodeError:
            refresh()
            pygame.display.update()
        STUN_COUNTER += 1
        if STUN_COUNTER == STUN_COUNTER_RESET:
            STUN_COUNTER = 0
