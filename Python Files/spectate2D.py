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
    IP = config["ip_address"]
    DIMS_SCALE = config["pixels_per_meter"]
    PLAYER_SCALE = config["player_size"]
    DISC_SCALE = config["disc_size"]
except FileNotFoundError:
    print("No config file found.")
    sys.exit()

# other globals
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 140, 0)
PURPLE = (238, 130, 238)

DIMS_ARENA = (30, 20, 80)
GDIST = DIMS_SCALE * 4
DIMS = (DIMS_ARENA[2] * DIMS_SCALE, DIMS_ARENA[0] * DIMS_SCALE)

SURFACE = None
FONT = None

stuncounter = 0
stun_counter_reset = 21


def draw_text(position, text):
    text = FONT.render(text, True, WHITE, None)
    text_rect = text.get_rect()
    text_rect.centerx = position[0]
    text_rect.centery = position[1]
    SURFACE.blit(text, text_rect)


def refresh():
    SURFACE.fill(BLACK)
    pygame.draw.line(SURFACE, WHITE, (10, 10), (DIMS[0] - 10, 10), 2)
    pygame.draw.line(SURFACE, WHITE, (10, 10), (10, DIMS[1] - 10), 2)
    pygame.draw.line(
        SURFACE, WHITE, (10, DIMS[1] - 10), (DIMS[0] - 10, DIMS[1] - 10), 2
    )
    pygame.draw.line(
        SURFACE, WHITE, (DIMS[0] - 10, 10), (DIMS[0] - 10, DIMS[1] - 10), 2
    )
    g1 = (
        (GDIST, SURFACE.get_rect().centery - 15),
        (GDIST, SURFACE.get_rect().centery + 15)
    )
    g2 = (
        (DIMS[0] - GDIST, SURFACE.get_rect().centery - 15),
        (DIMS[0] - GDIST, SURFACE.get_rect().centery + 15),
    )
    pygame.draw.line(SURFACE, BLUE, g1[0], g1[1], 2)
    pygame.draw.line(SURFACE, RED, g2[0], g2[1], 2)
    pygame.draw.line(
        SURFACE, BLUE, (SURFACE.get_rect().centerx - (4 * DIMS_SCALE), 10),
        (SURFACE.get_rect().centerx - (4 * DIMS_SCALE), DIMS[1]-10), 2)
    pygame.draw.line(
        SURFACE, RED, (SURFACE.get_rect().centerx + (4 * DIMS_SCALE), 10),
        (SURFACE.get_rect().centerx + (4 * DIMS_SCALE), DIMS[1] - 10), 2)


def coord_transform(position):
    x = (position[0] + DIMS_ARENA[0] / 2) * DIMS_SCALE
# y is unused
#   y = (position[1] + DIMS_ARENA[1] / 2) * DIMS_SCALE
    z = (position[2] + DIMS_ARENA[2] / 2) * DIMS_SCALE

    return int(z), int(x)


def draw_player(player, teamcolor):
    if player["stunned"] and (stuncounter < (stun_counter_reset/2)):
        return True
    position = coord_transform(player["position"])
    if player["possession"]:
        pygame.draw.circle(SURFACE, GREEN, position, 12*PLAYER_SCALE, 0)
    pygame.draw.circle(SURFACE, teamcolor, position, 10*PLAYER_SCALE, 0)
    ycolornum = 255*((player["position"][1]+10)/20)
    heightcolor = (ycolornum, ycolornum, ycolornum)
    pygame.draw.circle(SURFACE, heightcolor, position, 7*PLAYER_SCALE, 0)

# Names removed because I wanted less clutter
#   position2 = (position[0], position[1] - 12)
#   draw_text(position2, player["name"])


def draw_disc(disc):
    position = coord_transform(disc["position"])
    ycolornum = 255 * ((disc["position"][1] + 10) / 20)
    heightcolor = (ycolornum, ycolornum, ycolornum)
    pygame.draw.circle(SURFACE, WHITE, position, 7*DISC_SCALE, 0)
    pygame.draw.circle(SURFACE, heightcolor, position, 5*DISC_SCALE, 0)


def get_frame():
    content = json.loads(requests.get("http://"+IP+"/session").content)
    return content


def draw_frame(framedata):
    for team in framedata["teams"]:
        teamcolor = RED if "ORANGE" in team["team"] else BLUE
        for player in team["players"]:
            if player["name"] == framedata["client_name"]:
                teamcolor = PURPLE
            draw_player(player, teamcolor)
    draw_disc(framedata["disc"])
    draw_text((SURFACE.get_rect().centerx, 20), framedata["game_clock_display"])
    draw_text((20, 20), str(framedata["teams"][0]["stats"]["points"]))
    draw_text((DIMS[0] - 20, 20), str(framedata["teams"][1]["stats"]["points"]))


if __name__ == "__main__":
    pygame.init()

    SURFACE = pygame.display.set_mode(DIMS, 0, 32)
    FONT = pygame.font.SysFont(None, 20)
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
        stuncounter += 1
        if stuncounter == stun_counter_reset:
            stuncounter = 0