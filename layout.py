from typing import Optional

import numpy as np
import pygame
from pygame.locals import *

import config
from generator import SiteGenerator
from utils import Direction


class Line(pygame.sprite.Sprite):
    SPAN_UNIT = 32 * config.SCALING_FACTOR
    HALF_SPAN_UNIT = 16 * config.SCALING_FACTOR
    WIDTH = int(3 * config.SCALING_FACTOR)

    def __init__(self, x1, y1, x2, y2, direction, background):
        super().__init__()
        self.x1 = int(x1 * Line.SPAN_UNIT)
        self.y1 = int(y1 * Line.SPAN_UNIT)
        self.x2 = int(x2 * Line.SPAN_UNIT)
        self.y2 = int(y2 * Line.SPAN_UNIT)
        self.direction = direction
        self.rect = pygame.draw.line(background,
                                     config.FOREGROUND_COLOR, (self.y1, self.x1), (self.y2, self.x2), Line.WIDTH)

    def __hash__(self):
        return hash((self.x1, self.y1, self.x2, self.y2))

    def __eq__(self, other):
        if isinstance(other, Line):
            return self.x1 == other.x1 and self.y2 == other.y2 and self.x2 == other.x2 and self.y2 == other.y2
        else:
            return False

    def __str__(self):
        return f"Line({self.x1}, {self.y1}, {self.x2}, {self.y2}, {self.direction})"


class VisitedPlace(pygame.sprite.Sprite):
    def __init__(self, robot):
        super().__init__()
        self.position = robot.rect.center
        self.radius = robot.radius // 3
        self.rect = pygame.Rect(self.position[0] - self.radius, self.position[1] - self.radius,
                                robot.WIDTH, robot.WIDTH)

    def __hash__(self):
        return hash(self.position)

    def __eq__(self, other):
        if isinstance(other, VisitedPlace):
            return self.position == other.position
        else:
            return False


class RoomArea(pygame.sprite.Sprite):
    def __init__(self, room_id, x1, y1, x2, y2, background: pygame.Surface):
        super().__init__()
        self.id = room_id
        self.x1 = int(x1 * Line.SPAN_UNIT) + Line.WIDTH
        self.y1 = int(y1 * Line.SPAN_UNIT) + Line.WIDTH
        self.x2 = int(x2 * Line.SPAN_UNIT) - Line.WIDTH
        self.y2 = int(y2 * Line.SPAN_UNIT) - Line.WIDTH
        self.background = background
        self.rect = pygame.Rect(self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1)
        self.visited = False

    def update(self):
        pygame.draw.rect(self.background, config.VISITED_COLOR if self.visited else config.FAILED_VISIT_COLOR,
                         self.rect)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, RoomArea):
            return self.id == other.id
        else:
            return False

    def __bool__(self):
        return self.visited


class InjuryArea(pygame.sprite.Sprite):
    WIDTH = int(24 * config.SCALING_FACTOR)

    def __init__(self, injury_id, x1, y1, x2, y2, background: pygame.Surface):
        super().__init__()
        self.id = int(injury_id)
        self.x1 = int(x1 * Line.SPAN_UNIT) + Line.WIDTH
        self.y1 = int(y1 * Line.SPAN_UNIT) + Line.WIDTH
        self.x2 = int(x2 * Line.SPAN_UNIT) - Line.WIDTH
        self.y2 = int(y2 * Line.SPAN_UNIT) - Line.WIDTH
        self.background = background
        self.rect = pygame.Rect(self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1)
        self.rescued = False
        self.image = InjuryArea.AVAILABLE_IMAGES[self.id % len(InjuryArea.AVAILABLE_IMAGES)]
        background.blit(self.image, self.image.get_rect(center=self.rect.center))

    def update(self):
        pygame.draw.rect(self.background, config.RESCUED_COLOR if self.rescued else config.FAILED_RESCUE_COLOR,
                         self.rect)
        self.background.blit(self.image, self.image.get_rect(center=self.rect.center))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, RoomArea):
            return self.id == other.id
        else:
            return False

    def __bool__(self):
        return self.rescued


class Layout:
    """Simulation layout."""

    def __init__(self, site: np.ndarray, rooms: Optional[list] = None, injuries: Optional[list] = None):
        """
        Creating a layout from a numpy.ndarray of site,
        and an list of rooms and injuries which are optional.
        """
        row_cnt, col_cnt = site.shape
        size = int((col_cnt - 1) * Line.SPAN_UNIT), int((row_cnt - 1) * Line.SPAN_UNIT)

        pygame.init()
        pygame.display.set_caption("Simulation")
        self.display = pygame.display.set_mode(size)
        self.rect = self.display.get_rect()
        self.center = self.rect.center
        self.__layout = pygame.Surface(size)
        self.__layout.fill(config.BACKGROUND_COLOR)
        self.lines = pygame.sprite.Group()
        self.rooms = pygame.sprite.Group()
        self.injuries = pygame.sprite.Group()
        self.visited_places = pygame.sprite.Group()

        for i in range(row_cnt):
            wall_start = 0
            wall_started = False
            for j in range(col_cnt):
                if site[i, j] == ord("%"):
                    if not wall_started and j + 1 != col_cnt:
                        wall_started = True
                else:
                    if wall_started and wall_start < j - 1:
                        self.lines.add(Line(i, wall_start, i, j - 1, Direction.HORIZONTAL, self.__layout))
                    wall_started = False
                    wall_start = j + 1
            if wall_started and wall_start < col_cnt:
                self.lines.add(Line(i, wall_start, i, col_cnt - 1, Direction.HORIZONTAL, self.__layout))

        for j in range(col_cnt):
            wall_start = 0
            wall_started = False
            for i in range(row_cnt):
                if site[i, j] == ord("%"):
                    if not wall_started and i + 1 != row_cnt:
                        wall_started = True
                else:
                    if wall_started and wall_start < i - 1:
                        self.lines.add(Line(wall_start, j, i - 1, j, Direction.VERTICAL, self.__layout))
                    wall_started = False
                    wall_start = i + 1
            if wall_started and wall_start < row_cnt:
                self.lines.add(Line(wall_start, j, row_cnt - 1, j, Direction.VERTICAL, self.__layout))

        if rooms is not None:
            for i, room in enumerate(rooms):
                self.rooms.add(RoomArea(i + 1, *room, self.__layout))  # assert len(room) == 4

        if injuries is not None:
            InjuryArea.AVAILABLE_IMAGES = (
                pygame.transform.smoothscale(pygame.image.load("assets/ghost_blue.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)),
                pygame.transform.smoothscale(pygame.image.load("assets/ghost_green.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)),
                pygame.transform.smoothscale(pygame.image.load("assets/ghost_orange.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)),
                pygame.transform.smoothscale(pygame.image.load("assets/ghost_red.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)))
            for img in InjuryArea.AVAILABLE_IMAGES:
                img.set_colorkey(pygame.Color("black"), RLEACCEL)
            for i, injury in enumerate(injuries):
                self.injuries.add(InjuryArea(i + 1, *injury, self.__layout))

    @staticmethod
    def from_file(filename):
        """
        Factory method for creating a layout from a text file.
        TODO: Can be improved to automatically recognize rooms and injuries
              according to different characters from the text file.
        """
        with open(filename) as file:
            lines = file.read().strip().splitlines()
        site = np.zeros((len(lines), len(lines[0])))
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                site[i, j] = ord(char)
        return Layout(site)

    @staticmethod
    def from_generator(gen: SiteGenerator):
        """
        Factory method for creating a layout from a SiteGenerator.
        The interface provided from SiteGenerator is ugly, so we need some extra effort here.
        """
        rooms = []
        injuries = []
        for y1, y2, x1, x2 in gen.rooms:
            if ord("0") <= gen.site_array[y1 + 2, x1 + 2] <= ord("9"):
                injuries.append((x1 + 1, y1 + 1, x2 + 1, y2 + 1))
            else:
                rooms.append((x1 + 1, y1 + 1, x2 + 1, y2 + 1))
        assert len(injuries) == gen.injuries
        return Layout(gen.site_array, rooms, injuries)

    def update(self):
        """Redraw method that should be called for each frame."""
        # if all(self.rooms) and all(self.injuries):  # have been visited and rescued
        #     config.PAUSE = True
        self.display.blit(self.__layout, self.rect)
