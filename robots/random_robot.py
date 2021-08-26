import random

from robots.robot import Robot
from state import *


class RandomRobot(Robot):
    class JustStartedState(AbstractState):
        def __init__(self, robot):
            super().__init__(robot)

        def transfer_to_next_state(self):
            robot = self.get_robot()
            robot.attempt_go_front()
            if robot.is_colliding_wall():
                robot.turn_to_azimuth(random.randint(-179, 180))
            elif robot.is_colliding_another_robot():
                robot.turn_to_azimuth(random.randint(-179, 180))
            else:
                choice = random.choice((robot.turn_to_azimuth, robot.commit_go_front))
                if choice == robot.turn_to_azimuth:
                    robot.cancel_go_front()
                    choice(random.randint(-179, 180))
                else:
                    choice()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
