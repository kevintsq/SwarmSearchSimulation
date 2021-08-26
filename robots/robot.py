import random

import utils
from layout import *
from state import *


class Robot(pygame.sprite.Sprite):
    """Basic robot using Bug0-like algorithm."""

    WIDTH = int(24 * config.SCALING_FACTOR)
    SIZE = (WIDTH, WIDTH)
    radius = WIDTH // 2

    class JustStartedState(State):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            robot.turn_right(robot.azimuth % 90 - 90)  # TODO
            robot.state = robot.following_wall_state

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
            if robot.is_colliding_wall():
                self.transfer_when_colliding_wall()
            elif robot.is_colliding_another_robot():
                self.transfer_when_colliding_another_robot()
            else:
                robot.commit_go_front()

    class FollowingWallState(State):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            robot.collide_turn_function(90)

        def transfer_when_not_following_wall(self):
            robot = self.get_robot()
            robot.commit_go_front()
            robot.turn_to_azimuth(robot.original_azimuth)
            robot.state = robot.just_started_state

    def __init__(self, robot_id, group, background, position, azimuth=0):
        super().__init__()
        self.id: int = robot_id
        self.group: pygame.sprite.AbstractGroup = group
        self.background: Layout = background
        self.position = position

        self.color_name, color = utils.get_color()
        self.image = pygame.Surface(Robot.SIZE)
        self.image.fill(color)
        self.image.blit(pygame.transform.smoothscale(pygame.image.load("assets/pacman_mask.png").convert_alpha(), Robot.SIZE),
                        (0, 0), None, BLEND_RGBA_MIN)
        self.image.set_colorkey(pygame.Color("black"), RLEACCEL)
        self.original_image = self.image.copy()

        self.original_azimuth = azimuth
        self.turn_to_azimuth(azimuth)
        self.collide_turn_function = None

        self.just_started_state = self.JustStartedState(self)
        self.following_wall_state = self.FollowingWallState(self)
        self.state = self.just_started_state
        self.just_followed_wall: Optional[pygame.sprite.Sprite] = None
        self.in_room = False

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

    def turn_to_azimuth(self, azimuth):
        self.azimuth = utils.normalize_azimuth(azimuth)
        self.direction = utils.azimuth_to_direction(self.azimuth)
        self.image = pygame.transform.rotate(self.original_image, self.azimuth)
        self.rect = self.image.get_rect(center=self.position)
        assert isinstance(self.azimuth, int)
        print(f"[{self}] turned to {self.azimuth}, {self.direction}.")

    def turn_right(self, degree):
        """NOTE: First call will set self.collide_turn_function according to the degree."""
        if self.collide_turn_function is None:
            if 0 < degree < 180:
                self.collide_turn_function = self.turn_right
            elif -179 < degree < 0:
                self.collide_turn_function = self.turn_left
            else:
                raise Exception(f"Illegal degree ({degree}) to set self.collide_turn_function!")
        self.turn_to_azimuth(self.azimuth - degree)

    def turn_left(self, degree):
        """NOTE: First call will set self.collide_turn_function according to the degree."""
        if self.collide_turn_function is None:
            if 0 < degree < 180:
                self.collide_turn_function = self.turn_left
            elif -179 < degree < 0:
                self.collide_turn_function = self.turn_right
            else:
                raise Exception(f"Illegal degree ({degree}) to set self.collide_turn_function!")
        self.turn_to_azimuth(self.azimuth + degree)

    def turn_back(self):
        self.turn_to_azimuth(self.azimuth + 180)

    def attempt_go_front(self):
        """
        NOTE: DISTANCE SHOULDN'T BE TOO BIG,
              OTHERWISE IT WILL HAVE STRANGE BEHAVIOR DUE TO PRECISION LOSS OF FLOATING POINT NUMBERS!!!
        """
        self.old_rect = self.rect.copy()
        self.rect.move_ip(*utils.polar_to_pygame_cartesian(Robot.radius, self.azimuth))

    def cancel_go_front(self):
        self.rect = self.old_rect

    def commit_go_front(self):
        self.position = self.rect.center
        self.background.visited_places.add(VisitedPlace(self))

    def go_front_not_cancellable(self):
        self.rect.move_ip(*utils.polar_to_pygame_cartesian(Robot.radius, self.azimuth))
        self.position = self.rect.center

    def get_wall_rank(self, sprite: pygame.sprite.Sprite):
        wall = sprite.rect
        if self.direction == Direction.NORTH:
            return abs(wall.top - self.rect.bottom)
        elif self.direction == Direction.SOUTH:
            return abs(wall.bottom - self.rect.top)
        elif self.direction == Direction.WEST:
            return abs(wall.left - self.rect.right)
        elif self.direction == Direction.EAST:
            return abs(wall.right - self.rect.left)
        else:
            raise Exception(f"Robot [{self}] has invalid direction: {self.direction}.")

    def turn_according_to_wall(self):
        """NOTE: Updates self.just_followed_wall."""
        adjacent_walls = set(pygame.sprite.spritecollide(self.just_followed_wall, self.background.lines, False))
        # adjacent_walls.discard(self.just_followed_wall)
        self.just_followed_wall = min(adjacent_walls, key=self.get_wall_rank)
        wall = self.just_followed_wall.rect
        if self.direction == Direction.NORTH:
            if wall.left > self.rect.right:
                self.turn_right(90)
            else:
                self.turn_left(90)
        elif self.direction == Direction.SOUTH:
            if wall.left > self.rect.right:
                self.turn_left(90)
            else:
                self.turn_right(90)
        elif self.direction == Direction.WEST:
            if wall.top > self.rect.bottom:
                self.turn_left(90)
            else:
                self.turn_right(90)
        elif self.direction == Direction.EAST:
            if wall.top > self.rect.bottom:
                self.turn_right(90)
            else:
                self.turn_left(90)
        else:
            raise Exception(f"Robot [{self}] has invalid direction: {self.direction}.")

    def get_direction_according_to_others(self):
        vector = pygame.Vector2()
        for robot in self.group:
            if robot != self:
                vector += utils.pygame_cartesian_diff_vec(self.position, robot.rect.center)
        vector: pygame.Vector2 = -vector  # OK to use __neg__
        _, azimuth = vector.as_polar()
        return int(azimuth)

    def is_colliding_wall(self):
        self.collided_wall = pygame.sprite.spritecollideany(self, self.background.lines)
        return self.collided_wall

    def is_colliding_another_robot(self):
        for robot in self.group:
            if robot != self and pygame.sprite.collide_circle(robot, self):
                self.colliding_another_robot_count += 1
                return True
        return False

    def is_moving_along_wall(self):
        if self.just_followed_wall is None:  # Haven't followed a wall yet
            return True  # Regard it as following a wall
        wall = self.just_followed_wall.rect
        if self.direction == Direction.NORTH:
            distance = wall.top - self.rect.bottom
        elif self.direction == Direction.SOUTH:
            distance = self.rect.top - wall.bottom
        elif self.direction == Direction.WEST:
            distance = wall.left - self.rect.right
        elif self.direction == Direction.EAST:
            distance = self.rect.left - wall.right
        else:
            raise Exception(f"Robot [{self}] has invalid direction: {self.direction}.")
        return distance <= 0

    def is_revisiting_places(self):
        # return VisitedPlace(self) in self.background.visited_places
        return pygame.sprite.spritecollideany(VisitedPlace(self),
                                              self.background.visited_places, pygame.sprite.collide_circle)

    def __act_when_colliding_wall(self):
        """Not practical. Do not use."""
        self.cancel_go_front()
        self.just_followed_wall = self.collided_wall
        print(f"[{self}] Colliding {self.collided_wall}! Turning!")
        assert -180 < self.azimuth <= 180
        if self.collided_wall.direction == Direction.HORIZONTAL:
            if self.azimuth == -90 or self.azimuth == 90:
                random.choice((self.turn_left, self.turn_right))(self.azimuth)  # OK
            elif -90 < self.azimuth < 90:
                self.turn_right(self.azimuth)
            else:
                self.turn_right(self.azimuth - 180)
        elif self.collided_wall.direction == Direction.VERTICAL:
            if self.azimuth == 0 or self.azimuth == 180:
                random.choice((self.turn_left, self.turn_right))(90 - self.azimuth)  # OK
            elif 0 < self.azimuth <= 90:
                self.turn_left(90 - self.azimuth)
            elif 90 < self.azimuth < 180:
                self.turn_right(self.azimuth - 90)
            elif -90 < self.azimuth < 0:
                self.turn_right(90 - self.azimuth)
            else:
                self.turn_right(self.azimuth + 90)

    def update(self):
        """
        Redraw method that should be called for each frame.

        NOTE: Drawing rooms here instead of in the manager to prevent rooms' colors covering robots.
        """
        self.state.transfer_to_next_state()
        # self.next_action()
        self.action_count += 1
        entered_rooms = pygame.sprite.spritecollide(self, self.background.rooms, False)
        if len(entered_rooms) != 0:
            # self.in_room = True
            for room in entered_rooms:
                room.visited = True
                room.update()
        # else:
        #     self.in_room = False
        rescued_injuries = pygame.sprite.spritecollide(self, self.background.injuries, False)
        if len(rescued_injuries) != 0:
            # self.in_room = True
            for injury in rescued_injuries:
                injury.rescued = True
                injury.update()
        # else:
        #     self.in_room = False
        self.background.display.blit(self.image, self.rect)
