from abc import ABC, abstractmethod

from robot_manager import *


class AbstractRunner(ABC):
    @abstractmethod
    def run(self):
        pass


class StatisticRunner(AbstractRunner):
    def run(self):
        robot_cnt = 8
        logger.info(
            "site_width,site_height,room_cnt,injury_cnt,robot_type,robot_cnt,room_visited,injury_rescued,total_action_cnt,"
            f"{','.join(('robot_{}_visits,robot_{}_rescues,robot_{}_collides'.format(i, i, i) for i in range(robot_cnt)))}")
        for i in range(config.MAX_ITER):
            site_width, site_height, room_cnt, injury_cnt, robot_type = 120, 60, 120, 10, RobotUsingGas
            try:
                generator = SiteGenerator(site_width, site_height, room_cnt, injury_cnt)
            except:
                print(f"Generation {i} failed. Skipped.", file=sys.stderr)
                continue
            try:
                layout = Layout.from_generator(generator, enable_display=False)
                x, y = generator.departure_point
                manager = RandomSpreadingRobotManager(robot_type, layout, robot_cnt, (y * Wall.SPAN_UNIT, x * Wall.SPAN_UNIT))
                while True:
                    # if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                    if manager.action_count == 10000:
                        logger.info(f"{site_width},{site_height},{generator.room_cnt},{generator.injuries},"
                                    f"{robot_type.__name__},{robot_cnt},{layout.report()},{manager.report()}")
                        break
                    manager.update()
            except Exception:
                with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                    pickle.dump(generator, file)
                import traceback
                traceback.print_exc()


class DebugRunner(AbstractRunner):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        with open("debug/gen_dbg.pkl", "rb") as file:
            generator: SiteGenerator = pickle.load(file)
        layout = Layout.from_generator(generator)
        x, y = generator.departure_point
        manager = SpreadingRobotManager(RobotUsingGas, layout, 4, (y * Wall.SPAN_UNIT, x * Wall.SPAN_UNIT))
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        layout.update()
                        manager.update()
                        pygame.display.update()


class TestRunner(AbstractRunner):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        layout = Layout.from_file("assets/test.lay")
        manager = SpreadingRobotManager(RobotUsingGasAndSound, layout, 1, (100, 100))
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        layout.update()
                        manager.update()
                        pygame.display.update()


class PresentationRunner(AbstractRunner):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        generator = SiteGenerator(120, 60, 120, 10)
        try:
            layout = Layout.from_generator(generator)
            x, y = generator.departure_point
            manager = SpreadingRobotManager(RobotUsingGasAndSound, layout, 8, (y * Wall.SPAN_UNIT, x * Wall.SPAN_UNIT))
            clock = pygame.time.Clock()
            frame_rate = config.DISPLAY_FREQUENCY
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        with open("debug/gen_dbg.pkl", "wb") as file:
                            pickle.dump(generator, file)
                        pygame.quit()
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
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        with open("debug/gen_dbg.pkl", "rb") as file:
            generator: SiteGenerator = pickle.load(file)
        layout = Layout.from_generator(generator)
        x, y = generator.departure_point
        manager = RandomSpreadingRobotManager(RobotUsingGas, layout, 8, (y * Wall.SPAN_UNIT, x * Wall.SPAN_UNIT))
        clock = pygame.time.Clock()
        frame_rate = config.DISPLAY_FREQUENCY
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
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
        pygame.init()
        pygame.display.set_caption("Simulation")

    def run(self):
        robot_cnt = 6
        logger.info(
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
                x, y = generator.departure_point
                manager = SpreadingRobotManager(robot_type, layout, robot_cnt, (y * Wall.SPAN_UNIT, x * Wall.SPAN_UNIT))
                clock = pygame.time.Clock()
                frame_rate = config.DISPLAY_FREQUENCY
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            with open(f"debug/gen_dbg_{i}.pkl", "wb") as file:
                                pickle.dump(generator, file)
                            pygame.quit()
                            exit()
                        elif event.type == KEYDOWN:
                            if event.key == K_SPACE:
                                config.PAUSE = not config.PAUSE
                            if event.key == K_UP and frame_rate < config.DISPLAY_FREQUENCY:
                                frame_rate += 5
                            if event.key == K_DOWN and frame_rate > 5:
                                frame_rate -= 5
                    if all(layout.rooms) and all(layout.injuries):  # have been visited and rescued
                        logger.info(f"{site_width},{site_height},{room_cnt},{injury_cnt},{robot_type.__name__},"
                                    f"{robot_cnt},{layout.report()},{manager.report()}")
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
    runner = StatisticRunner()
    runner.run()
