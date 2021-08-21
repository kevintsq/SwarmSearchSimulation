from simulation import *

layout = Layout("empty_room.txt")
group = pygame.sprite.Group()
robot1 = Robot(1, group, layout, (400, 400))
group.add(robot1)
robot2 = Robot(2, group, layout, (800, 800))
group.add(robot2)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                layout.update()
                robot1.change_direction_according_to_other_robots()
                robot1.update()
                robot2.change_direction_according_to_other_robots()
                robot2.update()
                pygame.display.update()
