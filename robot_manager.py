from abc import ABC, abstractmethod

from robots.random_robot import *
from robots.robot import *
from robots.robot_using_gas import *
from robots.robot_using_sound import *
from robots.robot_using_gas_and_sound import *


class AbstractRobotManager(ABC):
    def __init__(self, robot_type, logger, background, depart_from_edge=False, initial_gather_mode=False):
        self.robots = pygame.sprite.Group()
        self.robot_type = robot_type
        self.logger = logger
        self.background: Layout = background
        self.amount = 0
        self.depart_from_edge = depart_from_edge
        self.initial_gather_mode = initial_gather_mode
        self.action_count = 0
        self.first_injury_action_count = 0

    @abstractmethod
    def add_robot(self, *args, **kwargs):
        """The manager must take care of the robot id."""

    def update(self):
        """Redraw method that should be called for each frame, but must after redrawing layout."""
        self.action_count += 1
        if self.initial_gather_mode and self.first_injury_action_count == 0 and any(self.robots):
            self.first_injury_action_count = self.action_count
        self.robots.update()
        pygame.display.set_caption(f"Action {self.action_count}")

    def enter_gathering_mode(self):
        self.first_injury_action_count = self.action_count
        for robot in self.robots:
            robot.state.transfer_when_need_to_gather()  # OK

    def report_search(self):
        report = [self.action_count - self.first_injury_action_count]
        for robot in self.robots:
            report += robot.report()  # OK
        return report

    def report_gather(self):
        count = 0
        for robot in self.robots:
            if robot.mission_complete:  # OK
                count += 1
        return count

    def __len__(self):
        return len(self.robots)

    def __iter__(self):
        return iter(self.robots)

    def __contains__(self, item):
        return item in self.robots

    def __str__(self):
        return str(self.robots)

    def __bool__(self):
        """all(self.robots) are mission_completed."""
        return all(self.robots)


class SpreadingRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, depart_from_edge=False, initial_gather_mode=False):
        super().__init__(robot_type, logger, background, depart_from_edge, initial_gather_mode)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = (180 if self.depart_from_edge else 360) * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy), azimuth, self.initial_gather_mode))
        self.amount += amount


class RandomSpreadingRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, depart_from_edge=False, initial_gather_mode=False):
        super().__init__(robot_type, logger, background, depart_from_edge, initial_gather_mode)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        initial_bias = random.randint(-179, 180)
        delta = (180 if self.depart_from_edge else 360) // amount
        for i in range(self.amount, self.amount + amount):
            azimuth = utils.normalize_azimuth(initial_bias + i * delta)
            if azimuth < 0:
                azimuth += 360
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy), azimuth, self.initial_gather_mode))
        self.amount += amount


class CollidingRobotManager(AbstractRobotManager):
    """Only for testing purpose."""

    def __init__(self, robot_type, logger, background, amount, depart_from_edge=False, initial_gather_mode=False):
        super().__init__(robot_type, logger, background, depart_from_edge, initial_gather_mode)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = (180 if self.depart_from_edge else 360) * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy),
                                            azimuth + 180, self.initial_gather_mode))
        self.amount += amount


class FreeRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, depart_from_edge=False, initial_gather_mode=False):
        super().__init__(robot_type, logger, background, depart_from_edge, initial_gather_mode)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = (180 if self.depart_from_edge else 360) * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy),
                                            initial_gather_mode=self.initial_gather_mode))
        self.amount += amount
