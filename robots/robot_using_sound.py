import utils
from robots.robot import Robot
from state import *


class RobotUsingSound(Robot):
    """Robot using Bug0-like algorithm with sound."""

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

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
            if robot.is_colliding_wall():
                self.transfer_when_colliding_wall()
            elif robot.is_colliding_another_robot():
                self.transfer_when_colliding_another_robot()
            elif robot.is_others_found_injuries():
                self.transfer_when_others_found_injuries()
            else:
                robot.commit_go_front()

    class GatheringState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            if robot.collide_turn_function is None:
                distance, robot.gathering_azimuth = robot.get_gathering_vector().as_polar()
                diff = utils.normalize_azimuth(robot.azimuth - robot.gathering_azimuth)
                robot.logger.debug(f"[{robot}] azimuth: {robot.gathering_azimuth}, self: {robot.azimuth}, diff: {diff}")
                if robot.azimuth % 90 == 0:
                    robot.turn_right(90 if diff > 0 else -90, update_collide_turn_func=True)
                else:
                    robot.turn_right(robot.azimuth % 90 if diff > 0 else robot.azimuth % 90 - 90, True)
                robot.attempt_go_front()
                if robot.is_colliding_wall():
                    robot.cancel_go_front()
                    robot.just_followed_wall = robot.collided_wall
                    robot.collide_turn_function(90)  # OK
                else:
                    distance2, azimuth = robot.get_gathering_vector().as_polar()
                    if distance2 > distance:
                        robot.cancel_go_front()
                        robot.turn_back(reset_collide_turn_func=True)
                    else:
                        robot.cancel_go_front()
            else:
                robot.collide_turn_function(90)

        def transfer_when_not_following_wall(self):
            robot = self.get_robot()
            robot.commit_go_front()
            robot.logger.debug(f"[{robot}] not following wall!")
            _, robot.gathering_azimuth = robot.get_gathering_vector().as_polar()
            robot.turn_to_azimuth(robot.gathering_azimuth)
            robot.just_followed_wall = None
            robot.collide_turn_function = None

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
            if robot.is_finish_gathering():
                robot.mission_complete = True
                robot.state = robot.found_injury_state
            if robot.is_colliding_wall():
                self.transfer_when_colliding_wall()
            elif robot.is_colliding_another_robot():
                self.transfer_when_colliding_another_robot()
            elif not robot.is_moving_along_wall():  # Needs Turning
                self.transfer_when_not_following_wall()
            else:
                robot.commit_go_front()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gathering_state = self.GatheringState(self)
