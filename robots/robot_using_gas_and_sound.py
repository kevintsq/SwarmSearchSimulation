from robots.robot_using_gas import *
from robots.robot_using_sound import *


class RobotUsingGasAndSound(RobotUsingGas, RobotUsingSound):
    """Robot using Bug1-like algorithm with sound."""

    class JustStartedState(RobotUsingSound.JustStartedState):
        def transfer_when_not_following_wall(self):
            robot: RobotUsingGasAndSound = self.get_robot()
            robot.commit_go_front()
            azimuth = robot.get_azimuth_according_to_others()
            if azimuth != utils.normalize_azimuth(robot.azimuth + 180) and azimuth != 0:
                robot.turn_to_azimuth(azimuth)
            else:
                robot.turn_to_azimuth(robot.original_azimuth)
            robot.just_followed_wall = None
            robot.collide_turn_function = None

    class FollowingWallState(RobotUsingGas.FollowingWallState, GatherableAbstractState):
        pass

    class GatheringState(GatherableRobot.GatheringState):
        def transfer_when_colliding_wall(self):
            super().transfer_when_colliding_wall()
            robot: RobotUsingGasAndSound = self.get_robot()
            if robot.is_revisiting_places() and robot.just_visited_place.visit_count >= 3:
                robot.turn_to_azimuth(random.randint(-179, 180))
                robot.just_visited_place.visit_count = 0
                robot.just_followed_wall = None
                robot.collide_turn_function = None
            elif robot.collide_turn_function is None:
                distance, robot.gathering_azimuth = robot.get_gathering_vector().as_polar()
                robot.gathering_azimuth = int(robot.gathering_azimuth)
                diff = utils.normalize_azimuth(robot.azimuth - (robot.gathering_azimuth + 180))
                # robot.logger.debug(f"[{robot}] azimuth: {robot.gathering_azimuth}, self: {robot.azimuth}, diff: {diff}")
                if robot.azimuth % 90 == 0:
                    robot.turn_right(90 if diff > 0 else -90, update_collide_turn_func=True)
                else:
                    robot.turn_right(robot.azimuth % 90 if diff > 0 else robot.azimuth % 90 - 90,
                                     update_collide_turn_func=True)
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

    def get_azimuth_according_to_others(self):
        if self.is_revisiting_places() and self.just_visited_place.visit_count >= 3:
            self.just_visited_place.visit_count = 0
            self.just_followed_wall = None
            self.collide_turn_function = None
            # return random.randint(-179, 180)
            self.original_azimuth = utils.normalize_azimuth(self.original_azimuth + 180)
            return self.original_azimuth  # may be modified
        else:
            vector = pygame.Vector2()
            for robot in self.group:
                if robot != self:
                    vector += utils.pygame_cartesian_diff_vec(self.position, robot.rect.center)
            vector: pygame.Vector2 = -vector  # OK to use __neg__
            _, azimuth = vector.as_polar()
            return int(azimuth)

    def get_weighted_azimuth_according_to_others(self):
        if self.is_revisiting_places() and self.just_visited_place.visit_count >= 3:
            self.just_visited_place.visit_count = 0
            self.just_followed_wall = None
            self.collide_turn_function = None
            # return random.randint(-179, 180)
            self.original_azimuth = utils.normalize_azimuth(self.original_azimuth + 180)
            return self.original_azimuth  # may be modified
        else:
            vector = pygame.Vector2()
            for robot in self.group:
                if robot != self:
                    diff_vec = utils.pygame_cartesian_diff_vec(self.position, robot.rect.center)
                    dist, _ = diff_vec.as_polar()
                    vector += diff_vec / dist
            vector: pygame.Vector2 = -vector
            _, azimuth = vector.as_polar()
            return int(azimuth)
