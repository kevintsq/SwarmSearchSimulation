import pickle
from multiprocessing import Pool, Lock

from psutil import cpu_count

from logger import *
from robot_manager import *


class AbstractRunner(ABC):
    def __init__(self, logger_type=LoggerType.SQLite3):
        self.logger_type = logger_type
        self.logger = Logger.get_logger(logger_type, reset=True)
        self.frame_rate = config.DISPLAY_FREQUENCY

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def should_quit(self, *args, **kwargs):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                # self.logger.stop()
                return
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    config.PAUSE = not config.PAUSE
                if event.key == K_UP and self.frame_rate < config.DISPLAY_FREQUENCY:
                    self.frame_rate += 5
                if event.key == K_DOWN and self.frame_rate > 5:
                    self.frame_rate -= 5


lock = Lock()


def run(i, site_width, site_height, generator, logger_type, depart_from_edge, robot_type, robot_cnt,
        max_search_action_cnt, max_return_action_cnt):
    with Logger(logger_type) as logger:
        try:
            layout = Layout.from_generator(generator, enable_display=False, depart_from_edge=depart_from_edge)
            manager = RandomSpreadingRobotManager(robot_type, logger, layout, robot_cnt,
                                                  depart_from_edge=depart_from_edge, initial_gather_mode=False)
            while not (layout or manager.action_count >= max_search_action_cnt):
                manager.update()
                if manager.action_count % 100 == 0:
                    logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
                               'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
                               'Search', *layout.report(), 0, *manager.report_search())
            logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
                       'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
                       'SearchFinished', *layout.report(), 0, *manager.report_search())
            if robot_type != Robot and robot_type != RobotUsingGas:
                manager.enter_gathering_mode()
                while not (manager or manager.action_count - manager.first_injury_action_count >= max_return_action_cnt):
                    manager.update()
                    if manager.action_count % 100 == 0:
                        logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
                                   'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
                                   'Return', *layout.report(), manager.report_gather(), *manager.report_search())
                logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
                           'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
                           'ReturnFinished', *layout.report(), manager.report_gather(), *manager.report_search())
        except:
            with lock:
                if not os.path.exists("debug"):
                    os.mkdir("debug")
            with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                pickle.dump(generator, file)
            import traceback
            traceback.print_exc()


class StatisticRunner(AbstractRunner):
    def __init__(self, logger_type):
        super().__init__(logger_type)

    @utils.timed
    def run(self):
        site_width, site_height, room_cnt, injury_cnt, max_search_action_cnt, max_return_action_cnt = \
            120, 60, 120, 10, 4000, 1000  # large
        # 80, 40, 60, 10, 2000, 500  # medium
        # 60, 30, 30, 10, 1000, 250  # small
        workers = []
        with Pool(cpu_count(logical=False)) as p:
            # Physical cores are used instead of logical ones because there are no benefits of using hyper-threading
            # on the latest Intel processors.
            for i in range(config.MAX_ITER):
                try:
                    generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
                except:
                    print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                    continue
                for robot_cnt in (2, 4, 6, 8, 10):
                    for robot_type in (RandomRobot, Robot, RobotUsingSound, RobotUsingGas, RobotUsingGasAndSound):
                        workers.append(p.apply_async(run, (
                                            i, site_width, site_height, generator, self.logger_type, False, robot_type,
                                            robot_cnt, max_search_action_cnt, max_return_action_cnt)))
                        workers.append(p.apply_async(run, (
                                            i, site_width, site_height, generator, self.logger_type, True, robot_type,
                                            robot_cnt, max_search_action_cnt, max_return_action_cnt)))
            cnt = len(workers)
            for i, worker in enumerate(workers):
                worker.wait()
                print(f"{i + 1:4} of {cnt} ({(i + 1) * 100 / cnt:6.2f}%) finished with status {worker.get()}.")


class GatheringStatisticRunner(AbstractRunner):
    def __init__(self, logger_type):
        super().__init__(logger_type)

    def run(self):
        robot_cnt = 8
        for i in range(config.MAX_ITER):
            site_width, site_height, room_cnt, injury_cnt, robot_type = 120, 60, 120, 1, RobotUsingGasAndSound
            try:
                generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
            except:
                print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                continue
            try:
                layout = Layout.from_generator(generator, enable_display=False, depart_from_edge=False)
                manager = RandomSpreadingRobotManager(robot_type, self.logger, layout, robot_cnt,
                                                      depart_from_edge=False, initial_gather_mode=True)
                while True:
                    if manager or manager.first_injury_action_count != 0 and \
                            manager.action_count - manager.first_injury_action_count >= 1000:
                        # all(robots) have mission-completed
                        # self.logger.log(site_width, site_height, generator.room_cnt, robot_type.__name__, robot_cnt,
                        #                 manager.report_gather())
                        break
                    manager.update()
            except:
                if not os.path.exists("debug"):
                    os.mkdir("debug")
                with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                    pickle.dump(generator, file)
                import traceback
                traceback.print_exc()


class DebugRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        with open("debug/gen_dbg.pkl", "rb") as file:
            generator: SiteGenerator = pickle.load(file)
        layout = Layout.from_generator(generator, depart_from_edge=False)
        manager = SpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 8,
                                        depart_from_edge=False, initial_gather_mode=False)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    # self.logger.stop()
                    return
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
        layout = Layout.from_file("assets/empty_room.lay")
        manager = RandomSpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 4,
                                              depart_from_edge=True, initial_gather_mode=False)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    # self.logger.stop()
                    return
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
        self.generator = SiteGenerator(40, 20, 30, 10)

    def run(self):
        try:
            layout = Layout.from_generator(self.generator, depart_from_edge=False)
            manager = SpreadingRobotManager(RobotUsingGas, self.logger, layout, 4,
                                            depart_from_edge=False, initial_gather_mode=False)
            clock = pygame.time.Clock()
            while not self.should_quit():
                if not config.PAUSE:
                    if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                        config.PAUSE = True
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(self.frame_rate)
        except:
            if not os.path.exists("debug"):
                os.mkdir("debug")
            with open("debug/gen_dbg.pkl", "wb") as file:
                pickle.dump(self.generator, file)
            import traceback
            traceback.print_exc()

    def should_quit(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                if not os.path.exists("debug"):
                    os.mkdir("debug")
                with open("debug/gen_dbg.pkl", "wb") as file:
                    pickle.dump(self.generator, file)
                pygame.quit()
                # self.logger.stop()
                return True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    config.PAUSE = not config.PAUSE
                if event.key == K_UP and self.frame_rate < config.DISPLAY_FREQUENCY:
                    self.frame_rate += 5
                if event.key == K_DOWN and self.frame_rate > 5:
                    self.frame_rate -= 5
        return False


class PresentationFileRunner(AbstractRunner):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        try:
            layout = Layout.from_file("assets/newmainbuildinghalfhalf.lay")
            manager = RandomSpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 4,
                                                  depart_from_edge=False, initial_gather_mode=False)
            clock = pygame.time.Clock()
            while not self.should_quit():
                if not config.PAUSE:
                    # if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                    #     config.PAUSE = True
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(self.frame_rate)
        except:
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
        layout = Layout.from_generator(generator, depart_from_edge=False)
        manager = RandomSpreadingRobotManager(RobotUsingGas, self.logger, layout, 10,
                                              depart_from_edge=False, initial_gather_mode=False)
        clock = pygame.time.Clock()
        frame_rate = config.DISPLAY_FREQUENCY
        while not self.should_quit():
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
        self.robot_cnt = 2
        site_width, site_height, room_cnt, injury_cnt, self.robot_type = 120, 60, 120, 10, RobotUsingGasAndSound
        self.generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)

    def run(self):
        try:
            layout = Layout.from_generator(self.generator, depart_from_edge=False)
            manager = RandomSpreadingRobotManager(self.robot_type, self.logger, layout, self.robot_cnt,
                                                  depart_from_edge=False, initial_gather_mode=False)
            clock = pygame.time.Clock()
            while not (layout or manager.action_count >= 500):
                if self.should_quit():
                    return
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(self.frame_rate)
            manager.enter_gathering_mode()
            while not (manager or manager.action_count - manager.first_injury_action_count >= 500):
                if self.should_quit():
                    return
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(self.frame_rate)
            while not self.should_quit():
                pass
        except:
            if not os.path.exists("debug"):
                os.mkdir("debug")
            with open(f"debug/gen_dbg.pkl", "wb") as file:
                pickle.dump(self.generator, file)
            import traceback
            traceback.print_exc()

    def should_quit(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                if not os.path.exists("debug"):
                    os.mkdir("debug")
                with open(f"debug/gen_dbg.pkl", "wb") as file:
                    pickle.dump(self.generator, file)
                pygame.quit()
                return True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    config.PAUSE = not config.PAUSE
                if event.key == K_UP and self.frame_rate < config.DISPLAY_FREQUENCY:
                    self.frame_rate += 5
                if event.key == K_DOWN and self.frame_rate > 5:
                    self.frame_rate -= 5
        return False


if __name__ == '__main__':
    runner = PresentationRunner()
    runner.run()
