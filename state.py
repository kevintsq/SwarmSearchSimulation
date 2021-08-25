class State:
    def __init__(self, robot):
        self.__robot = robot

    def get_robot(self):
        return self.__robot

    def transfer_to_next_state(self):
        pass

    def transfer_when_colliding_wall(self):
        self.__robot.cancel_go_front()
        self.__robot.just_followed_wall = self.__robot.collided_wall
        print(f"[{self.__robot}] Colliding wall! Turning!")

    def transfer_when_colliding_another_robot(self):
        self.__robot.cancel_go_front()
        print(f"[{self.__robot}] Colliding another robot! Turning!")
        self.__robot.turn_back()  # TODO
        self.__robot.state = self.__robot.just_started_state

    def transfer_when_not_following_wall(self):
        pass

    def transfer_when_revisiting_places(self):
        pass


