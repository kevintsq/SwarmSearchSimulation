from simulation import *

layout = Layout.from_file("assets/test.lay")
group = pygame.sprite.Group()
robot1 = RobotUsingGasAndSound(1, group, layout, (400, 200), -150)
group.add(robot1)                                # x     y
robot2 = RobotUsingGasAndSound(2, group, layout, (1600, 1000))
group.add(robot2)
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                layout.update()
                robot1.update()
                robot2.update()
                pygame.display.update()
