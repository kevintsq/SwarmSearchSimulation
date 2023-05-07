from abc import ABC, abstractmethod

from robots.random_robot import *
from robots.robot import *
from robots.robot_using_gas import *
from robots.robot_using_sound import *
from robots.robot_using_gas_and_sound import *


class AbstractRobotManager(ABC):
    def __init__(self, robot_type, logger, background, *, depart_from_edge=False, act_after_finding_injury=False):
        self.robots = pygame.sprite.Group()
        self.robot_type = robot_type
        self.logger = logger
        self.background: Layout = background
        self.amount = 0
        self.depart_from_edge = depart_from_edge
        self.act_after_finding_injury = act_after_finding_injury
        self.action_count = 0
        self.first_injury_action_count = 0
        self.last_just_start_count = 0
        self.last_following_wall_count = 0

    @abstractmethod
    def add_robot(self, *args, **kwargs):
        """The manager must take care of the robot id."""

    def update(self):
        """Redraw method that should be called for each frame, but must after redrawing layout."""
        self.action_count += 1
        if self.act_after_finding_injury and self.first_injury_action_count == 0 and any(self.robots):
            self.first_injury_action_count = self.action_count
        self.robots.update()
        pygame.display.set_caption(f"Action {self.action_count}")

    def enter_gathering_mode(self):
        self.first_injury_action_count = self.action_count
        for robot in self.robots:
            if isinstance(robot, GatherableRobot):
                robot.state.transfer_when_need_to_gather()

    def report_macro_states(self):
        just_started_cnt = 0
        following_wall_cnt = 0
        last_just_start_cnt = self.last_just_start_count
        last_following_wall_cnt = self.last_following_wall_count
        for robot in self.robots:
            if robot.state == robot.just_started_state:
                just_started_cnt += 1
            elif robot.state == robot.following_wall_state:
                following_wall_cnt += 1
        self.last_just_start_count = just_started_cnt
        self.last_following_wall_count = following_wall_cnt
        return self.action_count, just_started_cnt, following_wall_cnt,\
            just_started_cnt - last_just_start_cnt, following_wall_cnt - last_following_wall_cnt

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
    def __init__(self, robot_type, logger, background, amount, *,
                 depart_from_edge=False, act_after_finding_injury=False):
        super().__init__(robot_type, logger, background, depart_from_edge=depart_from_edge,
                         act_after_finding_injury=act_after_finding_injury)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        for i in range(amount):
            if self.depart_from_edge:
                azimuth = 180 * i // (amount - int(amount > 1))
            else:
                azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy), azimuth,
                                            act_after_finding_injury=self.act_after_finding_injury))
        self.amount += amount


class RandomSpreadingRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, *,
                 depart_from_edge=False, act_after_finding_injury=False):
        super().__init__(robot_type, logger, background, depart_from_edge=depart_from_edge,
                         act_after_finding_injury=act_after_finding_injury)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        initial_bias = random.randint(-179, 180)
        delta = (180 if self.depart_from_edge else 360) // amount
        for i in range(amount):
            azimuth = utils.normalize_azimuth(initial_bias + i * delta)
            if azimuth < 0:
                azimuth += 360  # OK
                # azimuth += 180 if self.depart_from_edge else 360
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy), azimuth,
                                            act_after_finding_injury=self.act_after_finding_injury))
        self.amount += amount


class CollidingRobotManager(AbstractRobotManager):
    """Only for testing purpose."""

    def __init__(self, robot_type, logger, background, amount, *,
                 depart_from_edge=False, act_after_finding_injury=False):
        super().__init__(robot_type, logger, background, depart_from_edge=depart_from_edge,
                         act_after_finding_injury=act_after_finding_injury)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        for i in range(amount):
            if self.depart_from_edge:
                azimuth = 180 * i // (amount - int(amount > 1))
            else:
                azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy),
                                            azimuth + 180, act_after_finding_injury=self.act_after_finding_injury))
        self.amount += amount


class FreeRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, *,
                 depart_from_edge=False, act_after_finding_injury=False):
        super().__init__(robot_type, logger, background, depart_from_edge=depart_from_edge,
                         act_after_finding_injury=act_after_finding_injury)
        self.add_robot(amount, self.background.departure_position)

    def add_robot(self, amount, position):
        for i in range(amount):
            if self.depart_from_edge:
                azimuth = 180 * i // (amount - int(amount > 1))
            else:
                azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT * 2), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background,
                                            (position[0] + dx, position[1] + dy),
                                            act_after_finding_injury=self.act_after_finding_injury))
        self.amount += amount
