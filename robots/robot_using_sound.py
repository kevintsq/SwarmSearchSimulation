from robots.robot import *
from state import *


class RobotUsingSound(Robot):
    """Robot using Bug0-like algorithm with sound."""

    class JustStartedState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot: RobotUsingSound = self.get_robot()
            azimuth = robot.get_azimuth_according_to_others()
            diff = utils.normalize_azimuth(robot.azimuth - (azimuth + 180))
            robot.logger.debug(f"[{robot}] azimuth: {azimuth}, self: {robot.azimuth}, diff: {diff}")
            if robot.azimuth % 90 == 0:
                robot.turn_right(90 if diff > 0 else -90, update_collide_turn_func=True)
            else:
                robot.turn_right(robot.azimuth % 90 if diff > 0 else robot.azimuth % 90 - 90, True)
            robot.state = robot.following_wall_state

        def transfer_to_next_state(self):
            robot: RobotUsingSound = self.get_robot()
            robot.attempt_go_front()
            if robot.is_colliding_wall():
                self.transfer_when_colliding_wall()
            elif robot.is_colliding_another_robot():
                self.transfer_when_colliding_another_robot()
            elif robot.is_others_found_injuries():
                self.transfer_when_need_to_gather()
            else:
                robot.commit_go_front()

    class GatheringState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot: RobotUsingSound = self.get_robot()
            if robot.collide_turn_function is None:
                distance, robot.gathering_azimuth = robot.get_gathering_vector().as_polar()
                robot.gathering_azimuth = int(robot.gathering_azimuth)
                diff = utils.normalize_azimuth(robot.azimuth - (robot.gathering_azimuth + 180))
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

        def transfer_when_colliding_another_robot(self):
            robot: RobotUsingSound = self.get_robot()
            robot.cancel_go_front()
            robot.logger.debug(f"[{robot}] Collides another robot! Turning!")
            robot.turn_right(90)  # TODO

        def transfer_when_not_following_wall(self):
            robot: RobotUsingSound = self.get_robot()
            robot.commit_go_front()
            robot.logger.debug(f"[{robot}] not following wall!")
            _, robot.gathering_azimuth = robot.get_gathering_vector().as_polar()
            robot.turn_to_azimuth(robot.gathering_azimuth)
            robot.just_followed_wall = None
            robot.collide_turn_function = None

        def transfer_to_next_state(self):
            robot: RobotUsingSound = self.get_robot()
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

    def get_azimuth_according_to_others(self):
        vector = pygame.Vector2()
        for robot in self.group:
            if robot != self:
                vector += utils.pygame_cartesian_diff_vec(self.position, robot.rect.center)
        vector: pygame.Vector2 = -vector  # OK to use __neg__
        _, azimuth = vector.as_polar()
        return int(azimuth)

    def get_farthest_vector(self, group):
        max_vector = pygame.Vector2()
        for robot in group:
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

    def get_nearest_door_vector(self) -> pygame.Vector2:
        door = min(self.background.doors,
                   key=lambda d: utils.pygame_cartesian_diff_vec(self.rect.center, d.position).length())
        return utils.pygame_cartesian_diff_vec(self.rect.center, door.position)

    def get_gathering_vector(self) -> pygame.Vector2:
        if self.in_room:
            return self.get_nearest_door_vector()
        else:
            return utils.pygame_cartesian_diff_vec(self.rect.center, self.gathering_position)