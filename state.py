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
        self.__robot.attempt_go_front()
        if self.__robot.is_colliding_wall():
            self.transfer_when_colliding_wall()
        elif self.__robot.is_colliding_another_robot():
            self.transfer_when_colliding_another_robot()
        elif not self.__robot.is_moving_along_wall():  # Needs Turning
            self.transfer_when_not_following_wall()
        else:
            self.__robot.commit_go_front()

    def transfer_when_colliding_wall(self):
        self.__robot.cancel_go_front()
        self.__robot.just_followed_wall = self.__robot.collided_wall
        self.__robot.logger.debug(f"[{self.__robot}] Collides wall! Turning!")

    def transfer_when_colliding_another_robot(self):
        self.__robot.cancel_go_front()
        self.__robot.logger.debug(f"[{self.__robot}] Collides another robot! Turning!")
        self.__robot.turn_right(90)  # TODO
        self.__robot.state = self.__robot.just_started_state

    def transfer_when_not_following_wall(self):
        self.__robot.commit_go_front()
        self.__robot.turn_according_to_wall()

    def transfer_when_revisiting_places(self):
        self.__robot.logger.debug(f"[{self.__robot}] Finds {self.__robot.position} has already been visited!")
