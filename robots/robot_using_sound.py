import utils
from robots.robot import Robot
from state import *


class RobotUsingSound(Robot):
    """Robot using Bug0-like algorithm with sound."""

    class JustStartedState(State):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            azimuth = robot.get_direction_according_to_others()
            diff = utils.normalize_azimuth(robot.azimuth - azimuth)
            print(f"[{robot}] azimuth: {azimuth}, self: {robot.azimuth}, diff: {diff}")
            if robot.azimuth % 90 == 0:
                robot.turn_right(90 if diff > 0 else -90, True)
            else:
                robot.turn_right(robot.azimuth % 90 if diff > 0 else robot.azimuth % 90 - 90, True)
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
            robot.just_followed_wall = None
            robot.state = robot.just_started_state

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
