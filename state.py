class AbstractState:
    """
    Abstract State with some default methods.
    All methods may be overridden by different states.
    """

    def __init__(self, robot):
        self.__robot = robot

    def get_robot(self):
        return self.__robot

    def transfer_to_next_state(self):
        """Default FSM that does not support gathering."""
        self.__robot.attempt_go_front()
        if self.__robot.is_colliding_wall():
            self.transfer_when_colliding_wall()
        elif self.__robot.is_colliding_another_robot():
            self.transfer_when_colliding_another_robot()
        elif not self.__robot.is_moving_along_wall():  # Needs Turning
            self.transfer_when_not_following_wall()
        elif self.__robot.has_found_injuries():
            self.transfer_when_found_injuries()
        else:
            self.__robot.commit_go_front()

    def transfer_when_colliding_wall(self):
        self.__robot.cancel_go_front()
        self.__robot.just_followed_wall = self.__robot.collided_wall
        # self.__robot.logger.debug(f"[{self.__robot}] Collides wall! Turning!")

    def transfer_when_colliding_another_robot(self):
        self.__robot.cancel_go_front()
        # self.__robot.logger.debug(f"[{self.__robot}] Collides another robot! Turning!")
        # if self.__robot.collide_turn_function == self.__robot.turn_left:  # judging turn_right first is also OK
        #     self.__robot.turn_left(90)
        # else:
        #     self.__robot.turn_right(90)
        self.__robot.turn_right(90)  # turn_left is also OK
        self.__robot.state = self.__robot.just_started_state

    def transfer_when_not_following_wall(self):
        self.__robot.commit_go_front()
        self.__robot.turn_according_to_wall()

    def transfer_when_revisiting_places(self):
        self.__robot.logger.debug(f"[{self.__robot}] Finds {self.__robot.position} has already been visited!")

    def transfer_when_found_injuries(self):
        self.__robot.commit_go_front()
        self.__robot.mission_complete = True
        self.__robot.state = self.__robot.found_injury_state

    def __str__(self):
        return self.__class__.__name__

    def __hash__(self):
        return hash(self.__class__.__name__)

    def __eq__(self, other):
        if isinstance(other, AbstractState):
            return self.__class__.__name__ == other.__class__.__name__
        else:
            return False


class GatherableAbstractState(AbstractState):
    def transfer_to_next_state(self):
        """Default FSM that supports gathering."""
        robot = self.get_robot()
        robot.attempt_go_front()
        if robot.is_colliding_wall():
            self.transfer_when_colliding_wall()
        elif robot.is_colliding_another_robot():
            self.transfer_when_colliding_another_robot()
        elif not robot.is_moving_along_wall():  # Needs Turning
            self.transfer_when_not_following_wall()
        elif robot.has_found_injuries():
            self.transfer_when_found_injuries()
        elif robot.others_have_found_injuries():
            self.transfer_when_need_to_gather()
        else:
            robot.commit_go_front()

    def transfer_when_need_to_gather(self):
        robot = self.get_robot()
        robot.commit_go_front()
        if not robot.act_after_finding_injury:
            robot.gathering_position = robot.background.departure_position
            robot.found_injuries = [robot.background.departure_place]
        robot.state = robot.gathering_state
        robot.collide_turn_function = None  # because need to be updated

    def transfer_when_finish_gathering(self):
        robot = self.get_robot()
        robot.commit_go_front()
        robot.mission_complete = True
        robot.state = robot.found_injury_state
