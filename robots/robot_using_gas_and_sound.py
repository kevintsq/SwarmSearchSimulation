from robots.robot import Robot
from state import *


class RobotUsingGasAndSound(Robot):
    """Robot using Bug1-like algorithm with sound."""

    class JustStartedState(State):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot = self.get_robot()
            robot.turn_right(robot.azimuth % 90 - 90)  # FIXME: Get direction from sound!
            # robot.cancel_go_front()
            # vector = pygame.Vector2()
            # for r in robot.group:
            #     if r != robot:
            #         vector += utils.pygame_cartesian_diff_vec(robot.position, robot.rect.center)
            # vector: pygame.Vector2 = -vector  # OK to use __neg__
            # _, azimuth = vector.as_polar()
            # robot.turn_to_azimuth(int(azimuth))
            # # robot.turn_back()
            # # robot.turn_to_azimuth(self.original_azimuth)
            # robot.just_followed_wall = None
            # robot.collide_turn_function = None
            robot.state = robot.following_wall_state

        def transfer_when_not_following_wall(self):
            robot = self.get_robot()
            robot.commit_go_front()
            robot.turn_to_azimuth(robot.original_azimuth)  # FIXME: Get direction from sound!

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
            if robot.is_colliding_wall():
                self.transfer_when_colliding_wall()
            elif robot.is_colliding_another_robot():
                self.transfer_when_colliding_another_robot()
            elif not robot.is_moving_along_wall():  # Needs Turning
                self.transfer_when_not_following_wall()
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
            if robot.is_revisiting_places():
                self.transfer_when_revisiting_places()
            else:
                robot.commit_go_front()
                robot.turn_according_to_wall()

        def transfer_when_revisiting_places(self):
            robot = self.get_robot()
            print(f"{robot.position} has already been visited!")
            robot.commit_go_front()
            robot.turn_according_to_wall()
            robot.state = robot.just_started_state

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
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
