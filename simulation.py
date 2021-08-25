import pickle

from robots.robot import *


class AbstractRobotManager:
    def __init__(self, background):
        self.robots = pygame.sprite.Group()
        self.background: Layout = background

    def add_robot(self, *args, **kwargs):
        """The manager must take care of the robot id."""
        pass

    def update(self):
        """Redraw method that should be called for each frame, but must after redrawing layout."""
        self.robots.update()

    def __len__(self):
        return len(self.robots)

    def __iter__(self):
        return iter(self.robots)

    def __contains__(self, item):
        return item in self.robots

    def __str__(self):
        return str(self.robots)


class SpreadingRobotManager(AbstractRobotManager):
    def __init__(self, background, amount, position):
        super().__init__(background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Line.SPAN_UNIT), azimuth)
            self.robots.add(Robot(i, self.robots, self.background, (position[0] + dx, position[1] + dy), azimuth))
        self.amount += amount


class CollidingRobotManager(AbstractRobotManager):
    def __init__(self, background, amount, position):
        super().__init__(background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Line.SPAN_UNIT), azimuth)
            self.robots.add(Robot(i, self.robots, self.background, (position[0] + dx, position[1] + dy), azimuth + 180))
        self.amount += amount


class FreeRobotManager(AbstractRobotManager):
    def __init__(self, background, amount, position):
        super().__init__(background)
        self.amount = 0
        self.add_robot(amount, position)

    def add_robot(self, amount, position):
        for i in range(self.amount, self.amount + amount):
            azimuth = 360 * i // amount
            dx, dy = utils.polar_to_pygame_cartesian(int(Line.SPAN_UNIT), azimuth)
            self.robots.add(Robot(i, self.robots, self.background, (position[0] + dx, position[1] + dy)))
        self.amount += amount


if __name__ == '__main__':
    if config.DEBUG_MODE:
        # with open("gen_dbg.pkl", "rb") as file:
        #     generator = pickle.load(file)
        # manager = SpreadingRobotManager(layout, 6, (y * Line.SPAN_UNIT, x * Line.SPAN_UNIT))
        layout = Layout.from_file("assets/layout.lay")
        manager = SpreadingRobotManager(layout, 1, (100, 100))
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
    else:
        generator = SiteGenerator(80, 40, 40, 10)
        try:
            # layout = Layout.from_generator(generator)
            # x, y = generator.departure_point
            # manager = SpreadingRobotManager(layout, 6, (y * Line.SPAN_UNIT, x * Line.SPAN_UNIT))
            layout = Layout.from_file("assets/layout.lay")
            manager = SpreadingRobotManager(layout, 6, layout.center)
            clock = pygame.time.Clock()
            frame_rate = config.DISPLAY_FREQUENCY
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        with open("gen_dbg.pkl", "wb") as file:
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
                if not config.PAUSE:
                    layout.update()
                    manager.update()
                    pygame.display.update()
                    clock.tick(frame_rate)
        except Exception as e:
            with open("gen_dbg.pkl", "wb") as file:
                pickle.dump(generator, file)
            import traceback
            traceback.print_exc()
