import pickle

from logger import *
from robot_manager import *


class AbstractRunner(ABC):
    def __init__(self):
        self.logger = Logger()
        self.logger.start()

    @abstractmethod
    def run(self):
        pass


class StatisticRunner(AbstractRunner):
    def __init__(self):
        super().__init__()

    def run(self):
        robot_cnt = 8
        self.logger.info(
            "no,site_width,site_height,room_cnt,injury_cnt,"
            "robot_type,robot_cnt,mode,room_visited,injury_rescued,returned,total_action_cnt,"
            f"{','.join(('robot_{}_visits,robot_{}_rescues,robot_{}_collides'.format(i, i, i) for i in range(robot_cnt)))}")
        for i in range(config.MAX_ITER):
            site_width, site_height, room_cnt, injury_cnt, robot_type = 120, 60, 120, 10, RobotUsingGasAndSound
            try:
                generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
            except:
                print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                continue
            try:
                layout = Layout.from_generator(generator, enable_display=False, depart_from_edge=False)
                manager = RandomSpreadingRobotManager(robot_type, self.logger, layout, robot_cnt,
                                                      initial_gather_mode=False)
                while not (layout or manager.action_count >= 3750):
                    manager.update()
                    if manager.action_count % 5 == 0:
                        self.logger.info(f"{i},{site_width},{site_height},{generator.room_cnt},{generator.injuries},"
                                         f"{robot_type.__name__},{robot_cnt},Search,{layout.report_search()},NA,"
                                         f"{manager.report_search()}")
                manager.enter_gathering_mode()
                while not (manager or manager.action_count - manager.first_injury_action_count >= 1000):
                    manager.update()
                    if manager.action_count % 5 == 0:
                        self.logger.info(f"{i},{site_width},{site_height},{generator.room_cnt},{generator.injuries},"
                                         f"{robot_type.__name__},{robot_cnt},Return,{layout.report_search()},"
                                         f"{manager.report_gather()},{manager.report_search()}")
            except:
                with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                    pickle.dump(generator, file)
                import traceback
                traceback.print_exc()
        self.logger.stop()


class GatheringStatisticRunner(AbstractRunner):
    def __init__(self):
        super().__init__()

    def run(self):
        robot_cnt = 8
        self.logger.info("site_width,site_height,room_cnt,robot_type,robot_cnt,total_action_cnt,total_returned_cnt")
        for i in range(config.MAX_ITER):
            site_width, site_height, room_cnt, injury_cnt, robot_type = 120, 60, 120, 1, RobotUsingGasAndSound
            try:
                generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
            except:
                print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                continue
            try:
                layout = Layout.from_generator(generator, enable_display=False)
                manager = RandomSpreadingRobotManager(robot_type, self.logger, layout, robot_cnt,
                                                      initial_gather_mode=True)
                while True:
                    if manager or manager.first_injury_action_count != 0 and \
                            manager.action_count - manager.first_injury_action_count >= 1000:
                        # all(robots) have mission-completed
                        self.logger.info(f"{site_width},{site_height},{generator.room_cnt},{robot_type.__name__},"
                                         f"{robot_cnt},{manager.report_gather()}")
                        break
                    manager.update()
            except:
                with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                    pickle.dump(generator, file)
                import traceback
                traceback.print_exc()
        self.logger.stop()


class DebugRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        with open("debug/gen_dbg.pkl", "rb") as file:
            generator: SiteGenerator = pickle.load(file)
        layout = Layout.from_generator(generator)
        manager = SpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 8, initial_gather_mode=False)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    self.logger.stop()
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        layout.update()
                        manager.update()
                        pygame.display.update()


class TestRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        layout = Layout.from_file("assets/test.lay")
        manager = SpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 1, initial_gather_mode=False)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    self.logger.stop()
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        layout.update()
                        manager.update()
                        pygame.display.update()


class PresentationRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        generator = SiteGenerator(120, 60, 120, 1)
        try:
            layout = Layout.from_generator(generator, depart_from_edge=True)
            manager = SpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 8,
                                            depart_from_edge=True, initial_gather_mode=False)
            clock = pygame.time.Clock()
            frame_rate = config.DISPLAY_FREQUENCY
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        with open("debug/gen_dbg.pkl", "wb") as file:
                            pickle.dump(generator, file)
                        pygame.quit()
                        self.logger.stop()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            config.PAUSE = not config.PAUSE
                        if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                            frame_rate += 5
                        if event.key == K_DOWN and frame_rate > 5:
                            frame_rate -= 5
                if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                    config.PAUSE = True
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(frame_rate)
        except:
            with open("debug/gen_dbg.pkl", "wb") as file:
                pickle.dump(generator, file)
            import traceback
            traceback.print_exc()


class DebugPresentationRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        with open("debug/gen_dbg.pkl", "rb") as file:
            generator: SiteGenerator = pickle.load(file)
        layout = Layout.from_generator(generator)
        manager = RandomSpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 8, initial_gather_mode=True)
        clock = pygame.time.Clock()
        frame_rate = config.DISPLAY_FREQUENCY
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    self.logger.stop()
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        config.PAUSE = not config.PAUSE
                    if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                        frame_rate += 5
                    if event.key == K_DOWN and frame_rate > 5:
                        frame_rate -= 5
            if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                config.PAUSE = True
            if not config.PAUSE:
                layout.update()
                manager.update()
                pygame.display.update()
                clock.tick(frame_rate)


class StatisticPresentationRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        robot_cnt = 6
        self.logger.info(
            "site_width,site_height,room_cnt,injury_cnt,robot_type,robot_cnt,room_visited,injury_rescued,total_action_cnt,"
            f"{','.join(('robot_{}_visits,robot_{}_rescues,robot_{}_collides'.format(i, i, i) for i in range(robot_cnt)))}")
        for i in range(config.MAX_ITER):
            site_width, site_height, room_cnt, injury_cnt, robot_type = 80, 40, 40, 10, RobotUsingGasAndSound
            try:
                generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
            except:
                print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                continue
            try:
                layout = Layout.from_generator(generator)
                manager = SpreadingRobotManager(robot_type, self.logger, layout, robot_cnt, initial_gather_mode=False)
                clock = pygame.time.Clock()
                frame_rate = config.DISPLAY_FREQUENCY
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                                pickle.dump(generator, file)
                            pygame.quit()
                            self.logger.stop()
                            exit()
                        elif event.type == KEYDOWN:
                            if event.key == K_SPACE:
                                config.PAUSE = not config.PAUSE
                            if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                                frame_rate += 5
                            if event.key == K_DOWN and frame_rate > 5:
                                frame_rate -= 5
                    if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                        self.logger.info(f"{site_width},{site_height},{room_cnt},{injury_cnt},{robot_type.__name__},"
                                         f"{robot_cnt},{layout.report_search()},{manager.report_search()}")
                        break
                    if not config.PAUSE:
                        layout.update()
                        manager.update()
                        pygame.display.update()
                        clock.tick(frame_rate)
            except Exception:
                with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                    pickle.dump(generator, file)
                import traceback
                traceback.print_exc()


if __name__ == '__main__':
    runner = PresentationRunner()
    runner.run()
