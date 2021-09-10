import pickle
import sys
from multiprocessing import Pool, Lock

from logger import *
from robot_manager import *


lock = Lock()


class AbstractRunner(ABC):
    def __init__(self):
        with lock:
            self.logger = Logger(reset=True)
        # self.logger.start()

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


def run(i, site_width, site_height, generator, depart_from_edge, robot_type, robot_cnt, max_search_action_cnt):
    try:
        with lock:
            logger = Logger()
        layout = Layout.from_generator(generator, enable_display=False, depart_from_edge=depart_from_edge)
        manager = RandomSpreadingRobotManager(robot_type, logger, layout, robot_cnt,
                                              depart_from_edge=depart_from_edge, initial_gather_mode=False)
        while not (layout or manager.action_count >= max_search_action_cnt):
            manager.update()
            if manager.action_count % 100 == 0:
                with lock:
                    logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
                               'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
                               'Search', *layout.report(), 0, *manager.report_search())
        with lock:
            logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
                       'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
                       'SearchFinished', *layout.report(), 0, *manager.report_search())
        # if robot_type != Robot and robot_type != RobotUsingGas:
        #     manager.enter_gathering_mode()
        #     while not (manager or manager.action_count - manager.first_injury_action_count >= max_return_action_cnt):
        #         manager.update()
        #         if manager.action_count % 100 == 0:
        #             with lock:
        #                 logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
        #                            'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
        #                            'Return', *layout.report(), manager.report_gather(), *manager.report_search())
        #     with lock:
        #         logger.log(i, site_width, site_height, generator.room_cnt, generator.injuries,
        #                    'Edge' if depart_from_edge else 'Center', robot_type.__name__, robot_cnt,
        #                    'ReturnFinished', *layout.report(), manager.report_gather(), *manager.report_search())
    except:
        with lock:
            if not os.path.exists("debug"):
                os.mkdir("debug")
        with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
            pickle.dump(generator, file)
        import traceback
        traceback.print_exc()
    finally:
        logger.close()


class StatisticRunner(AbstractRunner):
    def __init__(self):
        super().__init__()

    def run(self):
        site_width, site_height, room_cnt, injury_cnt, max_search_action_cnt = 120, 60, 120, 10, 4000
        workers = []
        with Pool() as p:
            for i in range(config.MAX_ITER):
                try:
                    generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
                except:
                    print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                    continue
                for robot_cnt in (2, 4, 6, 8, 10):
                    for robot_type in (RandomRobot, Robot, RobotUsingSound, RobotUsingGas, RobotUsingGasAndSound):
                        workers.append(p.apply_async(run, (
                            i, site_width, site_height, generator, False, robot_type, robot_cnt, max_search_action_cnt)))
                        workers.append(p.apply_async(run, (
                            i, site_width, site_height, generator, True, robot_type, robot_cnt, max_search_action_cnt)))
            cnt = len(workers)
            for i, worker in enumerate(workers):
                worker.wait()
                print(f"{i + 1} of {cnt} ({(i + 1) * 100 / cnt: .2f}%) finished with status {worker.get()}.")
        # self.logger.stop()


class GatheringStatisticRunner(AbstractRunner):
    def __init__(self):
        super().__init__()

    def run(self):
        robot_cnt = 8
        # self.logger.info("site_width,site_height,room_cnt,robot_type,robot_cnt,total_action_cnt,total_returned_cnt")
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
                        # self.logger.info(f"{site_width},{site_height},{generator.room_cnt},{robot_type.__name__},"
                        #                  f"{robot_cnt},{manager.report_gather()}")
                        break
                    manager.update()
            except:
                if not os.path.exists("debug"):
                    os.mkdir("debug")
                with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                    pickle.dump(generator, file)
                import traceback
                traceback.print_exc()
        # self.logger.stop()


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
        manager = SpreadingRobotManager(RobotUsingGasAndSound, self.logger, layout, 1,
                                        depart_from_edge=False, initial_gather_mode=False)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    # self.logger.stop()
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
        generator = SiteGenerator(60, 30, 30, 1)
        try:
            layout = Layout.from_generator(generator, depart_from_edge=False)
            manager = RandomSpreadingRobotManager(RobotUsingGas, self.logger, layout, 10,
                                                  depart_from_edge=False, initial_gather_mode=False)
            clock = pygame.time.Clock()
            frame_rate = config.DISPLAY_FREQUENCY
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        if not os.path.exists("debug"):
                            os.mkdir("debug")
                        with open("debug/gen_dbg.pkl", "wb") as file:
                            pickle.dump(generator, file)
                        pygame.quit()
                        # self.logger.stop()
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
            if not os.path.exists("debug"):
                os.mkdir("debug")
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
        layout = Layout.from_generator(generator, depart_from_edge=False)
        manager = RandomSpreadingRobotManager(RobotUsingGas, self.logger, layout, 10,
                                              depart_from_edge=False, initial_gather_mode=False)
        clock = pygame.time.Clock()
        frame_rate = config.DISPLAY_FREQUENCY
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    # self.logger.stop()
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
        robot_cnt = 2
        site_width, site_height, room_cnt, injury_cnt, robot_type = 120, 60, 120, 10, RobotUsingGasAndSound
        generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
        try:
            layout = Layout.from_generator(generator, depart_from_edge=False)
            manager = RandomSpreadingRobotManager(robot_type, self.logger, layout, robot_cnt,
                                                  depart_from_edge=False, initial_gather_mode=False)
            clock = pygame.time.Clock()
            frame_rate = config.DISPLAY_FREQUENCY
            while not (layout or manager.action_count >= 500):
                for event in pygame.event.get():
                    if event.type == QUIT:
                        if not os.path.exists("debug"):
                            os.mkdir("debug")
                        with open(f"debug/gen_dbg.pkl", "wb") as file:
                            pickle.dump(generator, file)
                        pygame.quit()
                        # self.logger.stop()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            config.PAUSE = not config.PAUSE
                        if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                            frame_rate += 5
                        if event.key == K_DOWN and frame_rate > 5:
                            frame_rate -= 5
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(frame_rate)
            manager.enter_gathering_mode()
            while not (manager or manager.action_count - manager.first_injury_action_count >= 500):
                for event in pygame.event.get():
                    if event.type == QUIT:
                        if not os.path.exists("debug"):
                            os.mkdir("debug")
                        with open(f"debug/gen_dbg.pkl", "wb") as file:
                            pickle.dump(generator, file)
                        pygame.quit()
                        # self.logger.stop()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            config.PAUSE = not config.PAUSE
                        if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                            frame_rate += 5
                        if event.key == K_DOWN and frame_rate > 5:
                            frame_rate -= 5
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(frame_rate)
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        if not os.path.exists("debug"):
                            os.mkdir("debug")
                        with open(f"debug/gen_dbg.pkl", "wb") as file:
                            pickle.dump(generator, file)
                        pygame.quit()
                        # self.logger.stop()
                        exit()
        except Exception:
            if not os.path.exists("debug"):
                os.mkdir("debug")
            with open(f"debug/gen_dbg.pkl", "wb") as file:
                pickle.dump(generator, file)
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    runner = StatisticRunner()
    runner.run()
