#!/usr/bin/env python3
import json
import pygame
import sys
from pygame.locals import *
import requests

global ERROR_CHECK_LOGS
DIMS_SCALE = 1
USE_BG_IMG = False
BG_IMG_FILE = "placeholder"
BG_OFFSET = [0, 0]
DIMS = [500, 500]
FONT_SIZE = 20
SESSION_NOT_FOUND = False
JSON_ERROR = False


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
    # sizes
    PLAYER_SIZES = config["sizes"]["player_size_config"]
    DISC_SIZES = config["sizes"]["disc_size_config"]
    DIMS_SCALE = config["sizes"]["pixels_per_meter"]
    PLAYER_SCALE = config["sizes"]["player_scale"]
    DISC_SCALE = config["sizes"]["disc_scale"]
    FONT_SIZE = config["sizes"]["font_size"]
    LINE_THICKNESS = config["sizes"]["line_thickness_if_no_background"]
    # elements
    SHOW_TIME = config["elements"]["show_time"]
    SHOW_NAMES = config["elements"]["show_names"]
    SHOW_SCORES = config["elements"]["show_scores"]
    SHOW_HEIGHT = config["elements"]["show_height_with_color"]
    SHOW_POSSESSION = config["elements"]["show_possession"]
    SHOW_STUNS = config["elements"]["show_stunned"]
    HOST_DIFFERENT_COLOR = config["elements"]["host_different_color"]
    # colors
    BACKGROUND_COLOR = config["colors"]["background_color"]
    OUTLINES_COLOR = config["colors"]["outlines_color"]
    DISC_COLOR = config["colors"]["disc_color"]
    TIMER_COLOR = config["colors"]["timer_color"]
    POINTS_COLOR = config["colors"]["points_color"]
    NAMES_COLOR = config["colors"]["names_color"]
    POSSESSION_COLOR = config["colors"]["possession_color"]
    STUNNED_COLOR = config["colors"]["stunned_color"]
    BLUE_TEAM_COLOR = config["colors"]["blue_team_color"]
    ORANGE_TEAM_COLOR = config["colors"]["orange_team_color"]
    HOST_COLOR_BLUE = config["colors"]["host_color_blue"]
    HOST_COLOR_ORANGE = config["colors"]["host_color_orange"]
    ERROR_COLOR = config["colors"]["error_message_color"]
    # background options
    USE_BG_IMG = config["background_image"]["use_background_image"]
    BG_IMG_FILE = config["background_image"]["image_file"]
    BG_OFFSET = config["background_image"]["offset_xy"]
    ERROR_CHECK_LOGS = False
except FileNotFoundError:
    print("No config file found. Try downloading the config file again.")
    ERROR_CHECK_LOGS = True
except KeyError:
    print("Error in config file. Try downloading the config file again.")
    ERROR_CHECK_LOGS = True

# other globals
if not ERROR_CHECK_LOGS:
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
    SURFACE.fill(BACKGROUND_COLOR)
    if USE_BG_IMG and (not (SESSION_NOT_FOUND or JSON_ERROR or ERROR_CHECK_LOGS)):
        SURFACE.blit(BG.image, BG.rect)
    elif not (SESSION_NOT_FOUND or JSON_ERROR or ERROR_CHECK_LOGS):
        pygame.draw.line(SURFACE, OUTLINES_COLOR, (10, 10), (DIMS[0] - 10, 10), LINE_THICKNESS)
        pygame.draw.line(SURFACE, OUTLINES_COLOR, (10, 10), (10, DIMS[1] - 10), LINE_THICKNESS)
        pygame.draw.line(
            SURFACE, OUTLINES_COLOR, (10, DIMS[1] - 10), (DIMS[0] - 10, DIMS[1] - 10), LINE_THICKNESS
        )
        pygame.draw.line(
            SURFACE, OUTLINES_COLOR, (DIMS[0] - 10, 10), (DIMS[0] - 10, DIMS[1] - 10), LINE_THICKNESS
        )
        g1 = (
            (G_DIST, SURFACE.get_rect().centery - (2*DIMS_SCALE)),
            (G_DIST, SURFACE.get_rect().centery + (2*DIMS_SCALE))
        )
        g2 = (
            (DIMS[0] - G_DIST, SURFACE.get_rect().centery - (2*DIMS_SCALE)),
            (DIMS[0] - G_DIST, SURFACE.get_rect().centery + (2*DIMS_SCALE)),
        )
        pygame.draw.line(SURFACE, BLUE_TEAM_COLOR, g1[0], g1[1], LINE_THICKNESS)
        pygame.draw.line(SURFACE, ORANGE_TEAM_COLOR, g2[0], g2[1], LINE_THICKNESS)
        pygame.draw.line(
            SURFACE, BLUE_TEAM_COLOR, (SURFACE.get_rect().centerx - (4 * DIMS_SCALE), 10),
            (SURFACE.get_rect().centerx - (4 * DIMS_SCALE), DIMS[1]-10), LINE_THICKNESS)
        pygame.draw.line(
            SURFACE, ORANGE_TEAM_COLOR, (SURFACE.get_rect().centerx + (4 * DIMS_SCALE), 10),
            (SURFACE.get_rect().centerx + (4 * DIMS_SCALE), DIMS[1] - 10), LINE_THICKNESS)


def coord_transform(position):
    x = (position[0] + (DIMS_ARENA[0] / 2)) * DIMS_SCALE
#   y is unused
#   y = (position[1] + (DIMS_ARENA[1] / 2)) * DIMS_SCALE
    z = (position[2] + (DIMS_ARENA[2] / 2)) * DIMS_SCALE

    return int(z), int(x)


def draw_player(player, team_color):
    global ERROR_CHECK_LOGS
    try:
        position = coord_transform(player["position"])
        if player["stunned"] and SHOW_STUNS:
            pygame.draw.circle(SURFACE, STUNNED_COLOR, position,
                               int(PLAYER_SIZES["stunned_indicator"] * PLAYER_SCALE), 0)
        if player["possession"] and SHOW_POSSESSION:
            pygame.draw.circle(SURFACE, POSSESSION_COLOR, position,
                               int(PLAYER_SIZES["possession_indicator"] * PLAYER_SCALE), 0)
        pygame.draw.circle(SURFACE, team_color, position, int(PLAYER_SIZES["player"] * PLAYER_SCALE), 0)
        if SHOW_HEIGHT:
            y_color_num = 255 * ((player["position"][1] + 10) / 20)
            height_color = (y_color_num, y_color_num, y_color_num)
            pygame.draw.circle(SURFACE, height_color, position, int(PLAYER_SIZES["height_indicator"]*PLAYER_SCALE), 0)
        if SHOW_NAMES:
            position2 = (position[0], position[1] - ((int(12*PLAYER_SCALE))+(FONT_SIZE/2)))
            draw_text(position2, player["name"], NAMES_COLOR)
    except KeyError:
        print("Error in config file. Try downloading the config file again.")
        ERROR_CHECK_LOGS = True


def draw_disc(disc):
    global ERROR_CHECK_LOGS
    try:
        pos = disc["position"]
        position = coord_transform(pos)
        pygame.draw.circle(SURFACE, DISC_COLOR, position, int(DISC_SIZES["disc"]*DISC_SCALE), 0)
        if SHOW_HEIGHT:
            y_color_num = 255 * ((disc["position"][1] + 10) / 20)
            height_color = (y_color_num, y_color_num, y_color_num)
            pygame.draw.circle(SURFACE, height_color, position, int(DISC_SIZES["height_indicator"]*DISC_SCALE), 0)
    except KeyError:
        print("Error in config file. Try downloading the config file again.")
        ERROR_CHECK_LOGS = True


def get_frame():
    global SESSION_NOT_FOUND
    try:
        content = json.loads(requests.get(FULL_PATH if OVERRIDE_IP else ("http://"+IP+":6721/session")).content)
        content["render_frame"] = True
        SESSION_NOT_FOUND = False
        return content
    except requests.exceptions.ConnectionError:
        if not SESSION_NOT_FOUND:
            print("Could not find an EchoVR session at {}.".format(FULL_PATH if OVERRIDE_IP else IP))
        SESSION_NOT_FOUND = True


def draw_frame(frame_data):
    if not (SESSION_NOT_FOUND or JSON_ERROR or ERROR_CHECK_LOGS):
        for team in frame_data["teams"]:
            team_color = ORANGE_TEAM_COLOR if ORANGE_TEAM_NAME in team["team"] else BLUE_TEAM_COLOR
            for player in team["players"]:
                if player["name"] == frame_data["client_name"] and HOST_DIFFERENT_COLOR:
                    team_color = HOST_COLOR_ORANGE if ORANGE_TEAM_NAME in team["team"] else HOST_COLOR_BLUE
                draw_player(player, team_color)
        draw_disc(frame_data["disc"])
        if SHOW_TIME:
            draw_text((SURFACE.get_rect().centerx, 20), frame_data["game_clock_display"], TIMER_COLOR)
        if SHOW_SCORES:
            draw_text((20, 20), str(frame_data["teams"][0]["stats"]["points"]), POINTS_COLOR)
            draw_text((DIMS[0] - 20, 20), str(frame_data["teams"][1]["stats"]["points"]), POINTS_COLOR)
    elif SESSION_NOT_FOUND:
        draw_text((SURFACE.get_rect().centerx, SURFACE.get_rect().centery), "No data to display", ERROR_COLOR)
    elif JSON_ERROR:
        draw_text((SURFACE.get_rect().centerx, SURFACE.get_rect().centery), "No match to display", ERROR_COLOR)
    elif ERROR_CHECK_LOGS:
        draw_text((SURFACE.get_rect().centerx, SURFACE.get_rect().centery), "Please check the output log", ERROR_COLOR)


if __name__ == "__main__":
    pygame.init()

    SURFACE = pygame.display.set_mode(DIMS, 0, 32)
    FONT = pygame.font.SysFont(None, (20 if ERROR_CHECK_LOGS else FONT_SIZE))
    pygame.display.set_caption("Echo VR Spectator")

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if not ERROR_CHECK_LOGS:
            try:
                frame = get_frame()
                refresh()
                draw_frame(frame)
                JSON_ERROR = False
                pygame.display.update()
            except json.decoder.JSONDecodeError:
                JSON_ERROR = True
                refresh()
                draw_frame(False)
                pygame.display.update()
        else:
            refresh()
            draw_frame(False)
            pygame.display.update()
