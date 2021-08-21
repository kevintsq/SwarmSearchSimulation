import sys
from typing import Optional
import pickle

import numpy as np
import pygame
from pygame.locals import *

import config
from generator import SiteGenerator
import utils
from utils import Direction


class AbstractRobotManager:
    def __init__(self, background):
        self.robots = pygame.sprite.Group()
        self.background: Layout = background

    def add_robot(self, *args, **kwargs):
        """The manager must take care of the robot id."""
        pass

    def update(self):
        """Redraw method that should be called for each frame, but must after redrawing layout."""
        self.robots.update()

    def __len__(self):
        return len(self.robots)

    def __iter__(self):
        return iter(self.robots)

    def __contains__(self, item):
        return item in self.robots

    def __str__(self):
        return str(self.robots)


class SpreadingRobotManager(AbstractRobotManager):
    def __init__(self, background, amount, position):
        super().__init__(background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Line.SPAN_UNIT), azimuth)
            self.robots.add(Robot(i, self.robots, self.background, (position[0] + dx, position[1] + dy), azimuth))
        self.amount += amount


class CollidingRobotManager(AbstractRobotManager):
    def __init__(self, background, amount, position):
        super().__init__(background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Line.SPAN_UNIT), azimuth)
            self.robots.add(Robot(i, self.robots, self.background, (position[0] + dx, position[1] + dy), azimuth + 180))
        self.amount += amount


class FreeRobotManager(AbstractRobotManager):
    def __init__(self, background, amount, position):
        super().__init__(background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Line.SPAN_UNIT), azimuth)
            self.robots.add(Robot(i, self.robots, self.background, (position[0] + dx, position[1] + dy)))
        self.amount += amount


class Robot(pygame.sprite.Sprite):
    def __init__(self, robot_id, group, background, position, azimuth=0):
        super().__init__()
        self.id: int = robot_id
        self.group: pygame.sprite.AbstractGroup = group
        self.background: Layout = background
        self.position = position

        width = int(24 * config.SCALING_FACTOR)
        self.radius = width // 2

        self.color_name, color = utils.get_color()
        self.image = pygame.Surface((width, width))
        self.image.fill(color)
        self.image.blit(pygame.transform.smoothscale(pygame.image.load("pacman_mask.png").convert_alpha(),
                                                     (width, width)),
                        (0, 0), None, BLEND_RGBA_MIN)
        self.image.set_colorkey(pygame.Color("black"), RLEACCEL)
        self.original_image = self.image.copy()

        self.__turn_to_azimuth(azimuth)

        self.just_followed_wall: Optional[pygame.sprite.Sprite] = None

        self.action_count = 0
        self.colliding_another_robot_count = 0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Robot):
            return self.id == other.id
        else:
            return False

    def __str__(self):
        return f"Robot {self.id} ({self.color_name})"

    def __turn_to_azimuth(self, azimuth):
        self.azimuth = utils.normalize_azimuth(azimuth)
        self.direction = utils.azimuth_to_direction(self.azimuth)
        self.image = pygame.transform.rotate(self.original_image, self.azimuth)
        self.rect = self.image.get_rect(center=self.position)
        assert isinstance(self.azimuth, int)
        print(f"[{self}] turned to {self.azimuth}, {self.direction}.")

    def __turn_right(self, degree=90):
        self.__turn_to_azimuth(self.azimuth - degree)

    def __turn_left(self, degree=90):
        self.__turn_to_azimuth(self.azimuth + degree)

    def change_direction_according_to_other_robots(self):
        vector = pygame.Vector2()
        for robot in self.group:
            if robot != self:
                vector += utils.pygame_cartesian_diff_vec(self.position, robot.rect.center)
        vector: pygame.Vector2 = -vector  # OK to use __neg__
        _, azimuth = vector.as_polar()
        self.__turn_to_azimuth(int(azimuth))
        self.just_followed_wall = None

    def collided_another_robot(self):
        for robot in self.group:
            if robot != self and pygame.sprite.collide_circle(robot, self):
                self.colliding_another_robot_count += 1
                return True
        return False

    def __is_moving_along_wall(self):
        if self.just_followed_wall is None:  # Haven't followed a wall yet
            return True  # Regard it as following a wall
        wall = self.just_followed_wall.rect
        if self.direction == Direction.NORTH:
            distance = wall.top - self.rect.bottom
        elif self.direction == Direction.SOUTH:
            distance = self.rect.top - wall.bottom
        elif self.direction == Direction.WEST:
            distance = wall.left - self.rect.right
        else:
            distance = self.rect.left - wall.right
        return distance <= 0

    def __get_wall_rank(self, sprite: pygame.sprite.Sprite):
        wall = sprite.rect
        if self.direction == Direction.NORTH:
            return abs(wall.top - self.rect.bottom)
        elif self.direction == Direction.SOUTH:
            return abs(wall.bottom - self.rect.top)
        elif self.direction == Direction.WEST:
            return abs(wall.left - self.rect.right)
        else:
            return abs(wall.right - self.rect.left)

    def __next_action(self, distance):
        self.action_count += 1
        old_rect = self.rect.copy()
        self.rect.move_ip(*utils.polar_to_pygame_cartesian(distance, self.azimuth))
        collided_wall = pygame.sprite.spritecollideany(self, self.background.lines)
        if collided_wall:
            self.rect = old_rect
            self.just_followed_wall = collided_wall
            print(f"[{self}] Colliding wall! Turning!")
            self.__turn_right(self.azimuth % 90 - 90)  # TODO
        elif self.collided_another_robot():
            self.rect = old_rect
            print(f"[{self}] Colliding another robot! Turning!")
            self.__turn_right(180)  # TODO
        else:
            self.position = self.rect.center
            if not self.__is_moving_along_wall():  # Needs Turning
                if self.position in self.background.visited_places:  # TODO: detect range to simulate gas
                    print(f"{self.position} has already been visited! Turning...")
                    self.change_direction_according_to_other_robots()
                    return
                else:
                    self.background.visited_places.add(self.position)
                adjacent_walls = set(pygame.sprite.spritecollide(self.just_followed_wall, self.background.lines, False))
                # adjacent_walls.discard(self.just_followed_wall)
                self.just_followed_wall = min(adjacent_walls, key=self.__get_wall_rank)
                wall = self.just_followed_wall.rect
                self.action_count += 1
                if self.direction == Direction.NORTH:
                    if wall.left > self.rect.right:
                        self.__turn_right(90)
                    else:
                        self.__turn_left(90)
                elif self.direction == Direction.SOUTH:
                    if wall.left > self.rect.right:
                        self.__turn_left(90)
                    else:
                        self.__turn_right(90)
                elif self.direction == Direction.WEST:
                    if wall.top > self.rect.bottom:
                        self.__turn_left(90)
                    else:
                        self.__turn_right(90)
                elif self.direction == Direction.EAST:
                    if wall.top > self.rect.bottom:
                        self.__turn_right(90)
                    else:
                        self.__turn_left(90)

    def update(self):
        """
        Redraw method that should be called for each frame.

        NOTE: DISTANCE FOR __next_action SHOULDN'T BE TOO BIG,
              OTHERWISE IT WILL HAVE STRANGE BEHAVIOR DUE TO PRECISION LOSS OF FLOATING POINT NUMBERS!!!
        """
        self.__next_action(self.radius)
        entered_rooms = pygame.sprite.spritecollide(self, self.background.rooms, False)
        if len(entered_rooms) != 0:
            for room in entered_rooms:
                room.visited = True
                room.update()
        rescued_injuries = pygame.sprite.spritecollide(self, self.background.injuries, False)
        if len(rescued_injuries) != 0:
            for injury in rescued_injuries:
                injury.rescued = True
                injury.update()
        self.background.display.blit(self.image, self.rect)


class Line(pygame.sprite.Sprite):
    SPAN_UNIT = 32 * config.SCALING_FACTOR
    HALF_SPAN_UNIT = 16 * config.SCALING_FACTOR
    WIDTH = int(3 * config.SCALING_FACTOR)

    def __init__(self, x1, y1, x2, y2, background):
        super().__init__()
        self.x1 = int(x1 * Line.SPAN_UNIT)
        self.y1 = int(y1 * Line.SPAN_UNIT)
        self.x2 = int(x2 * Line.SPAN_UNIT)
        self.y2 = int(y2 * Line.SPAN_UNIT)
        self.rect = pygame.draw.line(background,
                                     config.FOREGROUND_COLOR, (self.y1, self.x1), (self.y2, self.x2), Line.WIDTH)

    def __hash__(self):
        return hash((self.x1, self.y1, self.x2, self.y2))

    def __eq__(self, other):
        if isinstance(other, Line):
            return self.x1 == other.x1 and self.y2 == other.y2 and self.x2 == other.x2 and self.y2 == other.y2
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
        self.visited_places = set()

        for i in range(row_cnt):
            wall_start = 0
            wall_started = False
            for j in range(col_cnt):
                if site[i, j] == ord("%"):
                    if not wall_started and j + 1 != col_cnt:
                        wall_started = True
                else:
                    if wall_started and wall_start < j:
                        self.lines.add(Line(i, wall_start, i, j - 1, self.__layout))
                    wall_started = False
                    wall_start = j + 1
            if wall_started and wall_start < col_cnt:
                self.lines.add(Line(i, wall_start, i, col_cnt - 1, self.__layout))

        for j in range(col_cnt):
            wall_start = 0
            wall_started = False
            for i in range(row_cnt):
                if site[i, j] == ord("%"):
                    if not wall_started and i + 1 != row_cnt:
                        wall_started = True
                else:
                    if wall_started and wall_start < i:
                        self.lines.add(Line(wall_start, j, i - 1, j, self.__layout))
                    wall_started = False
                    wall_start = i + 1
            if wall_started and wall_start < row_cnt:
                self.lines.add(Line(wall_start, j, row_cnt - 1, j, self.__layout))

        if rooms is not None:
            for i, room in enumerate(rooms):
                self.rooms.add(RoomArea(i + 1, *room, self.__layout))  # assert len(room) == 4

        if injuries is not None:
            InjuryArea.AVAILABLE_IMAGES = (
                pygame.transform.smoothscale(pygame.image.load("ghost_blue.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)),
                pygame.transform.smoothscale(pygame.image.load("ghost_green.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)),
                pygame.transform.smoothscale(pygame.image.load("ghost_orange.png").convert_alpha(),
                                             (InjuryArea.WIDTH, InjuryArea.WIDTH)),
                pygame.transform.smoothscale(pygame.image.load("ghost_red.png").convert_alpha(),
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
        if all(self.rooms) and all(self.injuries):  # have been visited and rescued
            config.PAUSE = True
        self.display.blit(self.__layout, self.rect)


if __name__ == '__main__':
    # layout = Layout.from_file("layout.lay")
    if config.DEBUG_MODE:
        with open("gen_dbg.pkl", "rb") as file:
            generator = pickle.load(file)
    else:
        generator = SiteGenerator(40, 20, 20, 10)
    try:
        layout = Layout.from_generator(generator)
        manager = SpreadingRobotManager(layout, 6, layout.center)

        if config.DEBUG_MODE:
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            layout.update()
                            manager.update()
                            pygame.display.update()
        else:
            clock = pygame.time.Clock()
            frame_rate = config.DISPLAY_FREQUENCY
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            config.PAUSE = not config.PAUSE
                        if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                            frame_rate += 5
                        if event.key == K_DOWN and frame_rate > 5:
                            frame_rate -= 5
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(frame_rate)
    except Exception as e:
        with open("gen_dbg.pkl", "wb") as file:
            pickle.dump(generator, file)
        import traceback
        traceback.print_exc()
