import utils
from robots.robot import Robot
from state import *


class RobotUsingGasAndSound(Robot):
    """Robot using Bug1-like algorithm with sound."""

    class JustStartedState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            azimuth = robot.get_direction_according_to_others()
            diff = utils.normalize_azimuth(robot.azimuth - azimuth)
            robot.logger.debug(f"[{robot}] azimuth: {azimuth}, self: {robot.azimuth}, diff: {diff}")
            if robot.azimuth % 90 == 0:
                robot.turn_right(90 if diff > 0 else -90, True)
            else:
                robot.turn_right(robot.azimuth % 90 if diff > 0 else robot.azimuth % 90 - 90, True)
            robot.state = robot.following_wall_state

        def transfer_when_not_following_wall(self):
            robot = self.get_robot()
            robot.commit_go_front()
            azimuth = robot.get_direction_according_to_others()
            if azimuth != utils.normalize_azimuth(robot.azimuth + 180):
                robot.turn_to_azimuth(int(azimuth))
            else:
                robot.turn_to_azimuth(robot.original_azimuth)
            robot.just_followed_wall = None

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
