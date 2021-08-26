import random

from robots.robot import Robot
from state import *


class RobotUsingGas(Robot):
    """Robot using Bug1-like algorithm."""

    class JustStartedState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            robot.turn_right(robot.azimuth % 90 - 90, True)  # TODO
            robot.state = robot.following_wall_state

        def transfer_when_not_following_wall(self):
            robot = self.get_robot()
            robot.commit_go_front()
            if robot.just_visited_place is not None and robot.just_visited_place.visit_count >= 3:
                robot.just_visited_place.visit_count = 0
                robot.turn_to_azimuth(random.randint(-179, 180))
            else:
                robot.turn_to_azimuth(robot.original_azimuth)

    class FollowingWallState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            robot.collide_turn_function(90)

        def transfer_when_not_following_wall(self):
            robot = self.get_robot()
            if robot.is_revisiting_places():
                self.transfer_when_revisiting_places()
            else:
                robot.commit_go_front()
                robot.turn_according_to_wall()

        def transfer_when_revisiting_places(self):
            super().transfer_when_revisiting_places()
            robot = self.get_robot()
            robot.commit_go_front()
            robot.turn_according_to_wall()
            robot.state = robot.just_started_state

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
