import random

import utils
from layout import *
from state import *


class Robot(pygame.sprite.Sprite):
    """Basic robot using Bug0-like algorithm."""

    WIDTH = int(24 * config.SCALING_FACTOR)
    SIZE = (WIDTH, WIDTH)
    GATHER_THRESHOLD = WIDTH * 10
    radius = WIDTH // 2

    class JustStartedState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            robot.turn_right(robot.azimuth % 90 - 90, True)  # TODO
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

    class FollowingWallState(AbstractState):
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
            robot.just_followed_wall = None
            robot.state = robot.just_started_state

    class FoundInjuryState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
            if robot.mission_complete or robot.is_colliding_wall() or robot.is_colliding_another_robot():
                robot.cancel_go_front()
            elif robot.is_leaving_gathering_circle():
                robot.cancel_go_front()
            else:
                robot.commit_go_front()

    def __init__(self, robot_id, logger, group, background: Layout, position, azimuth=0):
        super().__init__()
        self.id: int = robot_id
        self.logger = logger
        self.group: pygame.sprite.AbstractGroup = group
        self.background = background
        self.position = position

        if background.display is not None:
            self.color_name, color = utils.get_color()
            self.image = pygame.Surface(Robot.SIZE)
            self.image.fill(color)
            self.image.blit(pygame.transform.smoothscale(pygame.image.load("assets/pacman_mask.png").convert_alpha(), Robot.SIZE),
                            (0, 0), None, BLEND_RGBA_MIN)
            self.image.set_colorkey(pygame.Color("black"), RLEACCEL)
            self.original_image = self.image.copy()

        self.just_started_state = self.JustStartedState(self)
        self.following_wall_state = self.FollowingWallState(self)
        self.found_injury_state = self.FoundInjuryState(self)
        self.state = self.just_started_state

        self.collided_wall = None
        self.just_followed_wall: Optional[pygame.sprite.Sprite] = None  # Only update after colliding wall.
        self.just_visited_place: Optional[pygame.sprite.Sprite] = None
        self.in_room = False

        self.original_azimuth = azimuth
        self.turn_to_azimuth(azimuth)
        self.collide_turn_function = None
        self.gathering_position = None
        self.gathering_azimuth = None

        self.action_count = 0
        self.colliding_others_count = 0
        self.visit_room_count = 0
        self.rescue_count = 0
        self.found_injuries = None
        self.mission_complete = False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Robot):
            return self.id == other.id
        else:
            return False

    def __str__(self):
        if self.background.display is not None:
            return f"Robot {self.id} ({self.color_name} in {self.state.__class__.__name__})"
        else:
            return f"Robot {self.id} (in {self.state.__class__.__name__})"

    def __bool__(self):
        return self.mission_complete

    def turn_to_azimuth(self, azimuth):
        self.azimuth = utils.normalize_azimuth(int(azimuth))
        self.direction = utils.azimuth_to_direction(self.azimuth)
        if self.background.display is not None:
            self.image = pygame.transform.rotate(self.original_image, self.azimuth)
            self.rect = self.image.get_rect(center=self.position)
        else:
            self.rect = pygame.Rect(self.position[0] - self.radius, self.position[1] - self.radius, self.radius * 2, self.radius * 2)
        self.old_rect = self.rect.copy()
        self.logger.debug(f"[{self}] Turns to {self.azimuth}, {self.direction}.")

    def turn_right(self, degree, update_collide_turn_func=False):
        if update_collide_turn_func:
            if 0 < degree < 180:
                self.collide_turn_function = self.turn_right
            elif -179 < degree < 0:
                self.collide_turn_function = self.turn_left
            else:
                raise Exception(f"[{self}] Illegal degree ({degree}) to set self.collide_turn_function!")
        self.turn_to_azimuth(self.azimuth - degree)

    def turn_left(self, degree, update_collide_turn_func=False):
        if update_collide_turn_func:
            if 0 < degree < 180:
                self.collide_turn_function = self.turn_left
            elif -179 < degree < 0:
                self.collide_turn_function = self.turn_right
            else:
                raise Exception(f"[{self}] Illegal degree ({degree}) to set self.collide_turn_function!")
        self.turn_to_azimuth(self.azimuth + degree)

    def turn_back(self, reset_collide_turn_func=False):
        if reset_collide_turn_func:
            if self.collide_turn_function == self.turn_left:
                self.collide_turn_function = self.turn_right
            elif self.collide_turn_function == self.turn_right:
                self.collide_turn_function = self.turn_left
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
            raise Exception(f"[{self}] has invalid direction: {self.direction}.")

    def turn_according_to_wall(self):
        """NOTE: Updates self.just_followed_wall."""
        adjacent_walls = set(pygame.sprite.spritecollide(self.just_followed_wall, self.background.walls, False))
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
            raise Exception(f"[{self}] has invalid direction: {self.direction}.")

    def get_farthest_vector(self):
        max_vector = pygame.Vector2()
        for robot in self.group:
            if robot != self:
                diff = utils.pygame_cartesian_diff_vec(self.rect.center, robot.rect.center)
                if diff.length() > max_vector.length():
                    max_vector = diff
        return max_vector

    def get_nearest_vector(self, group):
        min_vector = None
        for sprite in group:
            if sprite != self:
                diff = utils.pygame_cartesian_diff_vec(self.rect.center, sprite.rect.center)
                if min_vector is None or diff.length() < min_vector.length():
                    min_vector = diff
        return min_vector

    def get_direction_according_to_others(self):
        # if self.in_room:
        #     door = min(self.background.doors, key=lambda d: utils.pygame_cartesian_diff_vec(d.position, self.position).length())
        #     vector = utils.pygame_cartesian_diff_vec(door.position, self.position)
        # else:
        # vector = pygame.Vector2()
        # for robot in self.group:
        #     if robot != self:
        #         diff = utils.pygame_cartesian_diff_vec(self.position, robot.rect.center)
        #         if diff.length() > 64 * config.SCALING_FACTOR:
        #             vector += diff
        #         else:
        #             vector -= diff
        # vector: pygame.Vector2 = -vector  # OK to use __neg__
        # _, azimuth = vector.as_polar()
        # return int(azimuth)
        return random.randint(-179, 180)

    def is_colliding_wall(self):
        self.collided_wall = pygame.sprite.spritecollideany(self, self.background.walls)
        return self.collided_wall

    def is_colliding_another_robot(self):
        for robot in self.group:
            if robot != self and pygame.sprite.collide_circle(robot, self):
                self.colliding_others_count += 1
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
            raise Exception(f"[{self}] has invalid direction: {self.direction}.")
        return distance <= 0

    def is_revisiting_places(self):
        # return VisitedPlace(self) in self.background.visited_places
        place = pygame.sprite.spritecollideany(VisitedPlace(self),
                                               self.background.visited_places, pygame.sprite.collide_circle)
        if place is not None:
            place.visit_count += 1  # OK
            self.just_visited_place = place
        return place

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

    def is_found_injuries(self):
        self.found_injuries = pygame.sprite.spritecollide(self, self.background.injuries, False)
        return len(self.found_injuries) != 0

    def is_finish_gathering(self):
        return pygame.sprite.collide_circle(self, self.found_injuries[0]) or \
            utils.pygame_cartesian_diff_vec(self.position, self.found_injuries[0].rect.center).length() < Robot.GATHER_THRESHOLD

    def is_leaving_gathering_circle(self):
        return utils.pygame_cartesian_diff_vec(self.position, self.found_injuries[0].rect.center).length() > Robot.GATHER_THRESHOLD

    def get_gathering_vector(self) -> pygame.Vector2:
        if self.in_room:
            return self.get_nearest_vector(self.background.doors)
        else:
            return utils.pygame_cartesian_diff_vec(self.rect.center, self.gathering_position)

    def is_others_found_injuries(self):
        for robot in self.group:
            if robot != self and robot.state == self.found_injury_state:
                self.found_injuries = robot.found_injuries  # OK
                self.gathering_position = robot.rect.center
                _, self.gathering_azimuth = self.get_gathering_vector().as_polar()
                return True
        return False

    def update(self):
        """
        Take action and redraw robot to the display. Should be called for each frame.

        NOTE: Drawing rooms here instead of in the manager to prevent rooms' colors covering robots.
        """
        self.state.transfer_to_next_state()
        self.action_count += 1
        entered_rooms = pygame.sprite.spritecollide(self, self.background.rooms, False)
        # self.logger.debug(f"[{self}] entered_rooms == {entered_rooms}")
        # self.logger.debug(f"[{self}] in_room == {self.in_room}")
        if len(entered_rooms) != 0:
            self.in_room = True
            for room in entered_rooms:
                if not room.visited:  # OK
                    self.visit_room_count += 1
                    room.update()
        else:  # FIXME: need to change
            self.in_room = False
        if self.background.display is not None:
            self.background.display.blit(self.image, self.rect)

    def report(self):
        return f"{self.visit_room_count + self.rescue_count},{self.rescue_count},{self.colliding_others_count}"
