from robots.robot import *


class RobotUsingGas(Robot):
    """Robot using Bug1-like algorithm."""

    class JustStartedState(Robot.JustStartedState):
        def transfer_when_not_following_wall(self):
            robot: RobotUsingGas = self.get_robot()
            robot.commit_go_front()
            if robot.just_visited_place is not None and robot.just_visited_place.visit_count >= 3:
                robot.just_visited_place.visit_count = 0
                robot.original_azimuth = utils.normalize_azimuth(robot.original_azimuth + 180)
            robot.turn_to_azimuth(robot.original_azimuth)
            robot.just_followed_wall = None
            robot.collide_turn_function = None

    class FollowingWallState(Robot.FollowingWallState):
        def transfer_when_not_following_wall(self):
            robot: RobotUsingGas = self.get_robot()
            if robot.is_revisiting_places():
                self.transfer_when_revisiting_places()
            else:
                robot.commit_go_front()
                robot.turn_according_to_wall()

        def transfer_when_revisiting_places(self):
            # super().transfer_when_revisiting_places()
            robot: RobotUsingGas = self.get_robot()
            robot.commit_go_front()
            robot.turn_according_to_wall()
            robot.state = robot.just_started_state

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.just_visited_place: Optional[pygame.sprite.Sprite] = None

    def commit_go_front(self):
        self.position = self.rect.center
        self.background.visited_places.add(VisitedPlace(self))

    def is_revisiting_places(self):
        # return VisitedPlace(self) in self.background.visited_places
        place = pygame.sprite.spritecollideany(VisitedPlace(self),
                                               self.background.visited_places, pygame.sprite.collide_circle)
        if place is not None:
            place.visit_count += 1  # OK
            self.just_visited_place = place
        return place
