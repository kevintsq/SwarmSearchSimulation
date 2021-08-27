from robots.robot import *
from robots.robot_using_gas import *
from robots.robot_using_sound import *
from robots.robot_using_gas_and_sound import *
from robots.random_robot import *


class AbstractRobotManager:
    def __init__(self, robot_type, logger, background):
        self.robots = pygame.sprite.Group()
        self.robot_type = robot_type
        self.logger = logger
        self.background: Layout = background
        self.action_count = 0

    def add_robot(self, *args, **kwargs):
        """The manager must take care of the robot id."""
        pass

    def update(self):
        """Redraw method that should be called for each frame, but must after redrawing layout."""
        self.action_count += 1
        self.robots.update()

    def report(self):
        return f"{self.action_count},{','.join((robot.report() for robot in self.robots))}"  # OK

    def __len__(self):
        return len(self.robots)

    def __iter__(self):
        return iter(self.robots)

    def __contains__(self, item):
        return item in self.robots

    def __str__(self):
        return str(self.robots)


class SpreadingRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, position):
        super().__init__(robot_type, logger, background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background, (position[0] + dx, position[1] + dy), azimuth))
        self.amount += amount


class RandomSpreadingRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, position):
        super().__init__(robot_type, logger, background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        azimuth = random.randint(-179, 180)
        delta = 360 // amount
        for i in range(self.amount, self.amount + amount):
            tmp = azimuth + i * delta
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT), tmp)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background, (position[0] + dx, position[1] + dy), tmp))
        self.amount += amount


class CollidingRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, position):
        super().__init__(robot_type, logger, background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background, (position[0] + dx, position[1] + dy), azimuth + 180))
        self.amount += amount


class FreeRobotManager(AbstractRobotManager):
    def __init__(self, robot_type, logger, background, amount, position):
        super().__init__(robot_type, logger, background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Wall.SPAN_UNIT), azimuth)
            self.robots.add(self.robot_type(i, self.logger, self.robots, self.background, (position[0] + dx, position[1] + dy)))
        self.amount += amount
