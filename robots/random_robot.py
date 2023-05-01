from robots.robot import *


class RandomRobot(GatherableRobot):
    class JustStartedState(GatherableAbstractState):
        def transfer_to_next_state(self):
            robot: RandomRobot = self.get_robot()
            robot.attempt_go_front()
            if robot.is_colliding_wall() or robot.is_colliding_another_robot():
                robot.turn_to_azimuth(random.randint(-179, 180))
            elif robot.has_found_injuries():
                self.transfer_when_found_injuries()
            elif robot.others_have_found_injuries():
                self.transfer_when_need_to_gather()
            else:
                choice = random.choice((robot.turn_to_azimuth, robot.commit_go_front))
                if choice == robot.turn_to_azimuth:
                    robot.cancel_go_front()
                    choice(random.randint(-179, 180))
                else:
                    choice()

    class GatheringState(GatherableAbstractState):
        def transfer_to_next_state(self):
            robot: RandomRobot = self.get_robot()
            robot.attempt_go_front()
            if robot.has_finished_gathering():
                self.transfer_when_finish_gathering()
            elif robot.is_colliding_wall() or robot.is_colliding_another_robot():
                robot.turn_to_azimuth(random.randint(-179, 180))
            else:
                choice = random.choice((robot.turn_to_azimuth, robot.commit_go_front))
                if choice == robot.turn_to_azimuth:
                    robot.cancel_go_front()
                    choice(random.randint(-179, 180))  # OK
                else:
                    choice()
