# -*- coding: utf-8 -*-
"""
@Time : 2021/8/19 16:48
@Auth : jingyao Li
@File : generator.py
@IDE  : PyCharm
"""
import random

import numpy as np


class SiteGenerator:
    def __init__(self, width=40, height=20, room_num=30, injuries=10, *, delete_fill=False):
        self.site = []
        self.site_array = np.zeros((height, width))
        self.v_corridor = []
        self.h_corridor = []
        self.spaces = []  # [x_min, x_max, y_min, y_max]
        self.rooms = []  # [y1, x1, y2, x2]
        self.width = width
        self.height = height
        self.central_departure_point = []  # [x, y]
        self.edge_departure_point = []
        self.room_num = room_num
        self.room_cnt = 0
        self.injuries = injuries
        if self.injuries > self.room_num:
            raise Exception("injuries overweight room number!")

        self.room_min_length = 5
        self.cor_min_length = 2

        self.wall_sign = "%"
        self.outer_door_sign = "/"
        self.inner_door_sign = "#"
        self.corridor_sign = " "

        self.generate(delete_fill=delete_fill)

    def print(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                print(self.site[i][j], end="")
            print()
        print(f"\n{self.height} * {self.width} site generated!")
        print(f"{self.room_cnt} rooms generated! "
              f"range: [A, {chr(ord('A') + self.room_cnt - 1)}]")
        print(f"{self.injuries} injuries generated! range: [0, {self.injuries - 1}]")

    def delete_fill(self):
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.site[i][j] == self.wall_sign and self.deletable(i, j):
                    self.site[i][j] = " "
        for room in self.rooms:
            x_min = room[0]
            x_max = room[1]
            y_min = room[2]
            y_max = room[3]
            self.site[x_min + 1][y_min + 1] = self.wall_sign
            self.site[x_min + 1][y_max + 1] = self.wall_sign
            self.site[x_max + 1][y_min + 1] = self.wall_sign
            self.site[x_max + 1][y_max + 1] = self.wall_sign

    def print_original(self):
        for row in self.site:
            print("".join(row))
        print()

    def deletable(self, i, j):
        if self.site[i - 1][j] != self.wall_sign and self.site[i - 1][j] != self.corridor_sign:
            return False
        if self.site[i + 1][j] != self.wall_sign and self.site[i + 1][j] != self.corridor_sign:
            return False
        if self.site[i][j + 1] != self.wall_sign and self.site[i][j + 1] != self.corridor_sign:
            return False
        if self.site[i][j - 1] != self.wall_sign and self.site[i][j - 1] != self.corridor_sign:
            return False
        return True

    def generate(self, *, delete_fill=False):
        # 创建数组
        self.site = [[self.wall_sign for _ in range(self.width - 2)] for _ in range(self.height - 2)]
        # 生成走廊
        self.generate_corridor()
        # 检测空地
        self.detect_spaces()
        # 生成房间
        self.generate_room()
        # 生成伤员
        self.put_injuries()
        # 封闭
        self.enclose()
        if delete_fill:
            self.delete_fill()
        for i, line in enumerate(self.site):
            for j, char in enumerate(line):
                self.site_array[i, j] = ord(char)

    def generate_corridor(self):
        middle_cor_x_min = (self.height - 2) // 2 - 2
        middle_cor_x_max = (self.height - 2) // 2 + 1
        for i in range(middle_cor_x_min, middle_cor_x_max + 1):
            for j in range(self.width - 2):
                self.site[i][j] = self.corridor_sign

        middle_cor_y_min = (self.width - 2) // 2 - 2
        middle_cor_y_max = (self.width - 2) // 2 + 1
        for i in range(self.height - 2):
            for j in range(middle_cor_y_min, middle_cor_y_max + 1):
                self.site[i][j] = self.corridor_sign

        self.v_corridor.append([middle_cor_x_min, middle_cor_x_max])
        self.h_corridor.append([middle_cor_y_min, middle_cor_y_max])

        self.central_departure_point = [(middle_cor_x_min + middle_cor_x_max) / 2,
                                        (middle_cor_y_min + middle_cor_y_max) / 2]
        self.edge_departure_point = [(2 * self.height - 9) / 2, (middle_cor_y_min + middle_cor_y_max) / 2]

        v_cor_num = random.randint(int(self.height / 20), int(self.height / 10)) - 1
        num = 0
        x_ranges = [[middle_cor_x_max + 1, self.height - 3], [0, middle_cor_x_min - 1]]
        while num < v_cor_num and len(x_ranges):
            index = random.randint(0, len(x_ranges) - 1)
            x_range = x_ranges[index]
            x_min = x_range[0] + self.room_min_length + 1
            x_max = x_range[1] - self.room_min_length - self.cor_min_length - 1
            if x_min > x_max:
                del x_ranges[index]
                continue
            x = random.randint(x_min, x_max)
            width = random.randint(self.cor_min_length, 3)
            self.v_corridor.append([x, x + width - 1])
            new_range1 = [x_range[0], x - 1]
            new_range2 = [x + width, x_range[1]]
            if new_range1[1] - new_range1[0] >= 2 * (self.room_min_length + 3):
                x_ranges.append(new_range1)
            if new_range2[1] - new_range2[0] >= 2 * (self.room_min_length + 3):
                x_ranges.append(new_range2)
            del x_ranges[index]
            num += 1
            for i in range(x, x + width):
                for j in range(self.width - 2):
                    self.site[i][j] = self.corridor_sign

        h_cor_num = random.randint(int(self.width / 20), int(self.width / 10)) - 1
        num = 0
        y_ranges = [[middle_cor_y_max + 1, self.width - 3], [0, middle_cor_y_min - 1]]
        while num < h_cor_num and len(y_ranges):
            index = random.randint(0, len(y_ranges) - 1)
            y_range = y_ranges[index]
            y_min = y_range[0] + self.room_min_length + 1
            y_max = y_range[1] - self.room_min_length - self.cor_min_length - 1
            if y_min > y_max:
                del y_ranges[index]
                continue
            y = random.randint(y_min, y_max)
            width = random.randint(self.cor_min_length, 3)
            self.h_corridor.append([y, y + width - 1])
            new_range1 = [y_range[0], y - 1]
            new_range2 = [y + width, y_range[1]]
            if new_range1[1] - new_range1[0] >= 2 * (self.room_min_length + 3):
                y_ranges.append(new_range1)
            if new_range2[1] - new_range2[0] >= 2 * (self.room_min_length + 3):
                y_ranges.append(new_range2)
            del y_ranges[index]
            num += 1
            for j in range(y, y + width):
                for i in range(self.height - 2):
                    self.site[i][j] = self.corridor_sign

        # print("corridor generated!")
        self.h_corridor = sorted(self.h_corridor, key=lambda cor: cor[0])
        self.v_corridor = sorted(self.v_corridor, key=lambda cor: cor[0])

    def detect_spaces(self):
        for i in range(len(self.v_corridor)):
            for j in range(len(self.h_corridor)):
                x_min = self.v_corridor[i - 1][1] + 1 if i != 0 else 0
                x_max = self.v_corridor[i][0] - 1
                y_min = self.h_corridor[j - 1][1] + 1 if j != 0 else 0
                y_max = self.h_corridor[j][0] - 1
                self.spaces.append([x_min, x_max, y_min, y_max])
        y_min = self.h_corridor[-1][1] + 1
        y_max = self.width - 3
        for i in range(len(self.v_corridor)):
            x_min = self.v_corridor[i - 1][1] + 1 if i != 0 else 0
            x_max = self.v_corridor[i][0] - 1
            self.spaces.append([x_min, x_max, y_min, y_max])
        x_min = self.v_corridor[-1][1] + 1
        x_max = self.height - 3
        for j in range(len(self.h_corridor)):
            y_min = self.h_corridor[j - 1][1] + 1 if j != 0 else 0
            y_max = self.h_corridor[j][0] - 1
            self.spaces.append([x_min, x_max, y_min, y_max])
        self.spaces.append([self.v_corridor[-1][1] + 1, self.height - 3, self.h_corridor[-1][1] + 1, self.width - 3])

    def detect_edge(self, boundary):
        x_min = boundary[0]
        x_max = boundary[1]
        y_min = boundary[2]
        y_max = boundary[3]
        up_edge = []
        down_edge = []
        right_edge = []
        left_edge = []
        for i in range(x_min, x_max + 1):
            for j in range(y_min, y_max + 1):
                if self.site[i][j] == self.wall_sign:
                    if j + 1 <= self.width - 3:
                        if self.site[i][j + 1] == self.outer_door_sign:
                            up = 2
                        elif self.site[i][j + 1] == self.wall_sign:
                            up = 0
                        else:
                            up = 1
                    else:
                        up = 0
                    if j - 1 >= 0:
                        if self.site[i][j - 1] == self.outer_door_sign:
                            down = 2
                        elif self.site[i][j - 1] == self.wall_sign:
                            down = 0
                        else:
                            down = 1
                    else:
                        down = 0
                    if i + 1 <= self.height - 3:
                        if self.site[i + 1][j] == self.outer_door_sign:
                            right = 2
                        elif self.site[i + 1][j] == self.wall_sign:
                            right = 0
                        else:
                            right = 1
                    else:
                        right = 0
                    if i - 1 >= 0:
                        if self.site[i - 1][j] == self.outer_door_sign:
                            left = 2
                        elif self.site[i - 1][j] == self.wall_sign:
                            left = 0
                        else:
                            left = 1
                    else:
                        left = 0
                    if up + down + right + left == 1:
                        if up == 1:
                            up_edge.append([i, j])
                        elif down == 1:
                            down_edge.append([i, j])
                        elif right == 1:
                            right_edge.append([i, j])
                        else:
                            left_edge.append([i, j])
        return [up_edge, down_edge, left_edge, right_edge]

    def generate_room(self):
        num = 0
        black_lists = [[] for _ in range(len(self.spaces))]
        while num < self.room_num:
            number = chr(num + ord('A'))
            if not self.spaces:
                break
            i = random.randint(0, len(self.spaces) - 1)
            space = self.spaces[i]
            black_list = black_lists[i]
            edges = self.detect_edge(space)
            up_edge = edges[0]
            down_edge = edges[1]
            left_edge = edges[2]
            right_edge = edges[3]
            all_edges = up_edge + down_edge + left_edge + right_edge
            for edge in black_list:
                if edge in all_edges:
                    all_edges.remove(edge)
            if not all_edges:
                del self.spaces[i]
                del black_lists[i]
                continue
            door = all_edges[random.randint(0, len(all_edges) - 1)]
            door_x = door[0]
            door_y = door[1]
            outer_door = door_x == space[0] or door_x == space[1] or door_y == space[2] or door_y == space[3]
            if door in down_edge:
                if not self.generate_upside_room(space, door, number, outer_door):
                    black_lists[i].append(door)
                else:
                    num += 1
            elif door in up_edge:
                if not self.generate_downside_room(space, door, number, outer_door):
                    black_lists[i].append(door)
                else:
                    num += 1
            elif door in right_edge:
                if not self.generate_leftside_room(space, door, number, outer_door):
                    black_lists[i].append(door)
                else:
                    num += 1
            else:
                if not self.generate_rightside_room(space, door, number, outer_door):
                    black_lists[i].append(door)
                else:
                    num += 1
        self.room_cnt = num

    def generate_upside_room(self, boundary: list, door: list, number, outer_door: bool):
        door_x = door[0]
        door_y = door[1]
        y = door_y + 1
        for y in range(door_y + 1, self.width - 2):
            if self.site[door_x][y] != self.wall_sign:
                break
        max_width = y - door_y - 2
        if max_width <= 0:
            return False
        x_min = door_x
        x_max = door_x
        while x_min >= boundary[0] and self.site[x_min][door_y] == self.wall_sign:
            for y in range(door_y + 1, self.width - 2):
                if self.site[x_min][y] != self.wall_sign:
                    break
            if y - door_y - 2 < max_width:
                break
            x_min -= 1
        x_min += 1
        while x_max <= boundary[1] and self.site[x_max][door_y] == self.wall_sign:
            for y in range(door_y + 1, self.width - 2):
                if self.site[x_max][y] != self.wall_sign:
                    break
            if y - door_y - 2 < max_width:
                break
            x_max += 1
        x_max -= 1
        if x_max == door_x or x_min == door_x:
            return False
        room_x_min = random.randint(x_min, door_x - 1)
        room_x_max = random.randint(door_x + 1, x_max)
        room_y_max = random.randint(door_y + 2, door_y + max_width + 1)

        # print
        self.site[door_x][door_y] = self.outer_door_sign if outer_door else self.inner_door_sign
        for i in range(room_x_min + 1, room_x_max):
            for j in range(door_y + 1, room_y_max):
                self.site[i][j] = number
        # add
        self.rooms.append([room_x_min, room_x_max, door_y, room_y_max])
        return True

    def generate_downside_room(self, boundary: list, door: list, number, outer_door: bool):
        door_x = door[0]
        door_y = door[1]
        y = door_y - 1
        for y in range(door_y - 1, -1, -1):
            if self.site[door_x][y] != self.wall_sign:
                break
        max_width = door_y - y - 2
        if max_width <= 0:
            return False
        x_min = door_x
        x_max = door_x
        while x_min >= boundary[0] and self.site[x_min][door_y] == self.wall_sign:
            for y in range(door_y - 1, -1, -1):
                if self.site[x_min][y] != self.wall_sign:
                    break
            if door_y - y - 2 < max_width:
                break
            x_min -= 1
        x_min += 1
        while x_max <= boundary[1] and self.site[x_max][door_y] == self.wall_sign:
            for y in range(door_y - 1, -1, -1):
                if self.site[x_max][y] != self.wall_sign:
                    break
            if door_y - y - 2 < max_width:
                break
            x_max += 1
        x_max -= 1
        if x_max == door_x or x_min == door_x:
            return False
        room_x_min = random.randint(x_min, door_x - 1)
        room_x_max = random.randint(door_x + 1, x_max)
        room_y_min = random.randint(door_y - max_width - 1, door_y - 2)

        # print
        self.site[door_x][door_y] = self.outer_door_sign if outer_door else self.inner_door_sign
        for i in range(room_x_min + 1, room_x_max):
            for j in range(door_y - 1, room_y_min, -1):
                self.site[i][j] = number
        # add
        self.rooms.append([room_x_min, room_x_max, room_y_min, door_y])
        return True

    def generate_rightside_room(self, boundary: list, door: list, number, outer_door: bool):
        door_x = door[0]
        door_y = door[1]
        x = door_x + 1
        for x in range(door_x + 1, self.height - 2):
            if self.site[x][door_y] != self.wall_sign:
                break
        max_length = x - door_x - 2
        if max_length <= 0:
            return False
        y_min = door_y
        y_max = door_y
        while y_min >= boundary[2] and self.site[door_x][y_min] == self.wall_sign:
            for x in range(door_x + 1, self.height - 2):
                if self.site[x][y_min] != self.wall_sign:
                    break
            if x - door_x - 2 < max_length:
                break
            y_min -= 1
        y_min += 1
        while y_max <= boundary[3] and self.site[door_x][y_max] == self.wall_sign:
            for x in range(door_x + 1, self.height - 2):
                if self.site[x][y_max] != self.wall_sign:
                    break
            if x - door_x - 2 < max_length:
                break
            y_max += 1
        y_max -= 1
        if y_max == door_y or y_min == door_y:
            return False
        room_y_min = random.randint(y_min, door_y - 1)
        room_y_max = random.randint(door_y + 1, y_max)
        room_x_max = random.randint(door_x + 2, door_x + max_length + 1)

        # print
        self.site[door_x][door_y] = self.outer_door_sign if outer_door else self.inner_door_sign
        for i in range(door_x + 1, room_x_max):
            for j in range(room_y_min + 1, room_y_max):
                self.site[i][j] = number
        # add
        self.rooms.append([door_x, room_x_max, room_y_min, room_y_max])
        return True

    def generate_leftside_room(self, boundary: list, door: list, number, outer_door: bool):
        door_x = door[0]
        door_y = door[1]
        x = door_x - 1
        for x in range(door_x - 1, -1, -1):
            if self.site[x][door_y] != self.wall_sign:
                break
        max_length = door_x - x - 2
        if max_length <= 0:
            return False
        y_min = door_y
        y_max = door_y
        while y_min >= boundary[2] and self.site[door_x][y_min] == self.wall_sign:
            for x in range(door_x - 1, -1, -1):
                if self.site[x][y_min] != self.wall_sign:
                    break
            if door_x - x - 2 < max_length:
                break
            y_min -= 1
        y_min += 1
        while y_max <= boundary[3] and self.site[door_x][y_max] == self.wall_sign:
            for x in range(door_x - 1, -1, -1):
                if self.site[x][y_max] != self.wall_sign:
                    break
            if door_x - x - 2 < max_length:
                break
            y_max += 1
        y_max -= 1
        if y_max == door_y or y_min == door_y:
            return False
        room_y_min = random.randint(y_min, door_y - 1)
        room_y_max = random.randint(door_y + 1, y_max)
        room_x_min = random.randint(door_x - max_length - 1, door_x - 2)

        # print
        self.site[door_x][door_y] = self.outer_door_sign if outer_door else self.inner_door_sign
        for i in range(door_x - 1, room_x_min, -1):
            for j in range(room_y_min + 1, room_y_max):
                self.site[i][j] = number
        # add
        self.rooms.append([room_x_min, door_x, room_y_min, room_y_max])
        return True

    def put_injuries(self):
        room_numbers = list(range(ord('A'), ord('A') + self.room_cnt))
        for i in range(self.injuries):
            if not room_numbers:
                raise Exception("injuries put failed!\ninjuries overweight room number!")
            index = random.randint(0, len(room_numbers) - 1)
            room_number = room_numbers[index]
            for x in range(0, len(self.site)):
                for y in range(0, len(self.site[x])):
                    if self.site[x][y] == chr(room_number):
                        self.site[x][y] = str(i)
            del room_numbers[index]

    def enclose(self):
        for item in self.site:
            item.insert(0, self.wall_sign)
            item.append(self.wall_sign)
        self.site.insert(0, [self.wall_sign for _ in range(self.width)])
        self.site.append([self.wall_sign for _ in range(self.width)])
        self.central_departure_point = [pos + 1 for pos in self.central_departure_point]
        self.edge_departure_point = [pos + 1 for pos in self.edge_departure_point]


if __name__ == '__main__':
    gen = SiteGenerator(40, 20, 10, 10, delete_fill=True)
    gen.print_original()
    print(gen.rooms)
    print(gen.injuries)
