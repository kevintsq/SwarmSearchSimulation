from enum import Enum, auto
import math
import random

import pygame


class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    WEST = auto()
    EAST = auto()

    FRONT = auto()
    BACK = auto()
    LEFT = auto()
    RIGHT = auto()

    HORIZONTAL = auto()
    VERTICAL = auto()

    def __neg__(self):
        if self == Direction.NORTH:
            return Direction.SOUTH
        elif self == Direction.SOUTH:
            return Direction.NORTH
        elif self == Direction.WEST:
            return Direction.EAST
        elif self == Direction.EAST:
            return Direction.WEST

        elif self == Direction.FRONT:
            return Direction.BACK
        elif self == Direction.BACK:
            return Direction.FRONT
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT

        else:
            return self


def polar_to_pygame_cartesian(distance, azimuth):
    dx = distance * math.cos(math.radians(-azimuth))
    dy = distance * math.sin(math.radians(-azimuth))
    return dx, dy


def pygame_cartesian_to_polar(self, other):
    dx = other[0] - self[0]
    dy = self[1] - other[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    azimuth = math.degrees(math.atan2(dy, dx))
    return distance, azimuth


def pygame_cartesian_diff_vec(self, other):
    dx = other[0] - self[0]
    dy = self[1] - other[1]
    return pygame.Vector2(dx, dy)


def normalize_azimuth(azimuth):
    """Normalize azimuth to (-180, 180]."""
    if azimuth <= -180:
        return azimuth + 360
    elif azimuth > 180:
        return azimuth - 360
    else:
        return azimuth


def azimuth_to_direction(azimuth):
    if -45 < azimuth <= 45:
        return Direction.EAST
    elif 45 < azimuth <= 135:
        return Direction.NORTH
    elif -135 < azimuth <= 45:
        return Direction.SOUTH
    else:
        return Direction.WEST


def direction_to_azimuth(direction):
    if direction == Direction.EAST:
        return 0
    elif direction == Direction.NORTH:
        return 90
    elif direction == Direction.WEST:
        return 180
    elif direction == Direction.SOUTH:
        return -90


__original_colors = [('aliceblue', (240, 248, 255, 255)),
                     ('aquamarine', (127, 255, 212, 255)),
                     # ('aquamarine1', (127, 255, 212, 255)),
                     # ('aquamarine2', (118, 238, 198, 255)),
                     # ('aquamarine3', (102, 205, 170, 255)),
                     # ('aquamarine4', (69, 139, 116, 255)),
                     ('azure', (240, 255, 255, 255)),
                     # ('azure1', (240, 255, 255, 255)),
                     # ('azure2', (224, 238, 238, 255)),
                     # ('azure3', (193, 205, 205, 255)),
                     # ('azure4', (131, 139, 139, 255)),
                     ('beige', (245, 245, 220, 255)),
                     ('bisque', (255, 228, 196, 255)),
                     # ('bisque1', (255, 228, 196, 255)),
                     # ('bisque2', (238, 213, 183, 255)),
                     # ('bisque3', (205, 183, 158, 255)),
                     # ('bisque4', (139, 125, 107, 255)),
                     ('blanchedalmond', (255, 235, 205, 255)),
                     ('blue', (0, 0, 255, 255)),
                     # ('blue1', (0, 0, 255, 255)),
                     # ('blue2', (0, 0, 238, 255)),
                     # ('blue3', (0, 0, 205, 255)),
                     # ('blue4', (0, 0, 139, 255)),
                     ('blueviolet', (138, 43, 226, 255)),
                     ('brown', (165, 42, 42, 255)),
                     # ('brown1', (255, 64, 64, 255)),
                     # ('brown2', (238, 59, 59, 255)),
                     # ('brown3', (205, 51, 51, 255)),
                     # ('brown4', (139, 35, 35, 255)),
                     ('burlywood', (222, 184, 135, 255)),
                     # ('burlywood1', (255, 211, 155, 255)),
                     # ('burlywood2', (238, 197, 145, 255)),
                     # ('burlywood3', (205, 170, 125, 255)),
                     # ('burlywood4', (139, 115, 85, 255)),
                     ('cadetblue', (95, 158, 160, 255)),
                     # ('cadetblue1', (152, 245, 255, 255)),
                     # ('cadetblue2', (142, 229, 238, 255)),
                     # ('cadetblue3', (122, 197, 205, 255)),
                     # ('cadetblue4', (83, 134, 139, 255)),
                     ('chartreuse', (127, 255, 0, 255)),
                     # ('chartreuse1', (127, 255, 0, 255)),
                     # ('chartreuse2', (118, 238, 0, 255)),
                     # ('chartreuse3', (102, 205, 0, 255)),
                     # ('chartreuse4', (69, 139, 0, 255)),
                     ('chocolate', (210, 105, 30, 255)),
                     # ('chocolate1', (255, 127, 36, 255)),
                     # ('chocolate2', (238, 118, 33, 255)),
                     # ('chocolate3', (205, 102, 29, 255)),
                     # ('chocolate4', (139, 69, 19, 255)),
                     ('coral', (255, 127, 80, 255)),
                     # ('coral1', (255, 114, 86, 255)),
                     # ('coral2', (238, 106, 80, 255)),
                     # ('coral3', (205, 91, 69, 255)),
                     # ('coral4', (139, 62, 47, 255)),
                     ('cornflowerblue', (100, 149, 237, 255)),
                     ('cornsilk', (255, 248, 220, 255)),
                     # ('cornsilk1', (255, 248, 220, 255)),
                     # ('cornsilk2', (238, 232, 205, 255)),
                     # ('cornsilk3', (205, 200, 177, 255)),
                     # ('cornsilk4', (139, 136, 120, 255)),
                     ('cyan', (0, 255, 255, 255)),
                     # ('cyan1', (0, 255, 255, 255)),
                     # ('cyan2', (0, 238, 238, 255)),
                     # ('cyan3', (0, 205, 205, 255)),
                     # ('cyan4', (0, 139, 139, 255)),
                     # ('darkblue', (0, 0, 139, 255)),
                     # ('darkcyan', (0, 139, 139, 255)),
                     # ('darkgoldenrod', (184, 134, 11, 255)),
                     # # ('darkgoldenrod1', (255, 185, 15, 255)),
                     # # ('darkgoldenrod2', (238, 173, 14, 255)),
                     # # ('darkgoldenrod3', (205, 149, 12, 255)),
                     # # ('darkgoldenrod4', (139, 101, 8, 255)),
                     # ('darkgreen', (0, 100, 0, 255)),
                     # ('darkkhaki', (189, 183, 107, 255)),
                     # ('darkmagenta', (139, 0, 139, 255)),
                     # ('darkolivegreen', (85, 107, 47, 255)),
                     # # ('darkolivegreen1', (202, 255, 112, 255)),
                     # # ('darkolivegreen2', (188, 238, 104, 255)),
                     # # ('darkolivegreen3', (162, 205, 90, 255)),
                     # # ('darkolivegreen4', (110, 139, 61, 255)),
                     # ('darkorange', (255, 140, 0, 255)),
                     # # ('darkorange1', (255, 127, 0, 255)),
                     # # ('darkorange2', (238, 118, 0, 255)),
                     # # ('darkorange3', (205, 102, 0, 255)),
                     # # ('darkorange4', (139, 69, 0, 255)),
                     # ('darkorchid', (153, 50, 204, 255)),
                     # # ('darkorchid1', (191, 62, 255, 255)),
                     # # ('darkorchid2', (178, 58, 238, 255)),
                     # # ('darkorchid3', (154, 50, 205, 255)),
                     # # ('darkorchid4', (104, 34, 139, 255)),
                     # ('darkred', (139, 0, 0, 255)),
                     # ('darksalmon', (233, 150, 122, 255)),
                     # ('darkseagreen', (143, 188, 143, 255)),
                     # # ('darkseagreen1', (193, 255, 193, 255)),
                     # # ('darkseagreen2', (180, 238, 180, 255)),
                     # # ('darkseagreen3', (155, 205, 155, 255)),
                     # # ('darkseagreen4', (105, 139, 105, 255)),
                     # ('darkslateblue', (72, 61, 139, 255)),
                     # ('darkturquoise', (0, 206, 209, 255)),
                     # ('darkviolet', (148, 0, 211, 255)),
                     # ('deeppink', (255, 20, 147, 255)),
                     # ('deeppink1', (255, 20, 147, 255)),
                     # ('deeppink2', (238, 18, 137, 255)),
                     # ('deeppink3', (205, 16, 118, 255)),
                     # ('deeppink4', (139, 10, 80, 255)),
                     ('deepskyblue', (0, 191, 255, 255)),
                     # ('deepskyblue1', (0, 191, 255, 255)),
                     # ('deepskyblue2', (0, 178, 238, 255)),
                     # ('deepskyblue3', (0, 154, 205, 255)),
                     # ('deepskyblue4', (0, 104, 139, 255)),
                     ('dodgerblue', (30, 144, 255, 255)),
                     # ('dodgerblue1', (30, 144, 255, 255)),
                     # ('dodgerblue2', (28, 134, 238, 255)),
                     # ('dodgerblue3', (24, 116, 205, 255)),
                     # ('dodgerblue4', (16, 78, 139, 255)),
                     ('firebrick', (178, 34, 34, 255)),
                     # ('firebrick1', (255, 48, 48, 255)),
                     # ('firebrick2', (238, 44, 44, 255)),
                     # ('firebrick3', (205, 38, 38, 255)),
                     # ('firebrick4', (139, 26, 26, 255)),
                     ('forestgreen', (34, 139, 34, 255)),
                     ('gainsboro', (220, 220, 220, 255)),
                     ('gold', (255, 215, 0, 255)),
                     # ('gold1', (255, 215, 0, 255)),
                     # ('gold2', (238, 201, 0, 255)),
                     # ('gold3', (205, 173, 0, 255)),
                     # ('gold4', (139, 117, 0, 255)),
                     ('goldenrod', (218, 165, 32, 255)),
                     # ('goldenrod1', (255, 193, 37, 255)),
                     # ('goldenrod2', (238, 180, 34, 255)),
                     # ('goldenrod3', (205, 155, 29, 255)),
                     # ('goldenrod4', (139, 105, 20, 255)),
                     ('green', (0, 255, 0, 255)),
                     # ('green1', (0, 255, 0, 255)),
                     # ('green2', (0, 238, 0, 255)),
                     # ('green3', (0, 205, 0, 255)),
                     # ('green4', (0, 139, 0, 255)),
                     ('greenyellow', (173, 255, 47, 255)),
                     ('honeydew', (240, 255, 240, 255)),
                     # ('honeydew1', (240, 255, 240, 255)),
                     # ('honeydew2', (224, 238, 224, 255)),
                     # ('honeydew3', (193, 205, 193, 255)),
                     # ('honeydew4', (131, 139, 131, 255)),
                     ('hotpink', (255, 105, 180, 255)),
                     # ('hotpink1', (255, 110, 180, 255)),
                     # ('hotpink2', (238, 106, 167, 255)),
                     # ('hotpink3', (205, 96, 144, 255)),
                     # ('hotpink4', (139, 58, 98, 255)),
                     ('indianred', (205, 92, 92, 255)),
                     # ('indianred1', (255, 106, 106, 255)),
                     # ('indianred2', (238, 99, 99, 255)),
                     # ('indianred3', (205, 85, 85, 255)),
                     # ('indianred4', (139, 58, 58, 255)),
                     ('khaki', (240, 230, 140, 255)),
                     # ('khaki1', (255, 246, 143, 255)),
                     # ('khaki2', (238, 230, 133, 255)),
                     # ('khaki3', (205, 198, 115, 255)),
                     # ('khaki4', (139, 134, 78, 255)),
                     ('lavender', (230, 230, 250, 255)),
                     ('lavenderblush', (255, 240, 245, 255)),
                     # ('lavenderblush1', (255, 240, 245, 255)),
                     # ('lavenderblush2', (238, 224, 229, 255)),
                     # ('lavenderblush3', (205, 193, 197, 255)),
                     # ('lavenderblush4', (139, 131, 134, 255)),
                     ('lawngreen', (124, 252, 0, 255)),
                     ('lemonchiffon', (255, 250, 205, 255)),
                     # ('lemonchiffon1', (255, 250, 205, 255)),
                     # ('lemonchiffon2', (238, 233, 191, 255)),
                     # ('lemonchiffon3', (205, 201, 165, 255)),
                     # ('lemonchiffon4', (139, 137, 112, 255)),
                     # ('lightblue', (173, 216, 230, 255)),
                     # # ('lightblue1', (191, 239, 255, 255)),
                     # # ('lightblue2', (178, 223, 238, 255)),
                     # # ('lightblue3', (154, 192, 205, 255)),
                     # # ('lightblue4', (104, 131, 139, 255)),
                     # ('lightcoral', (240, 128, 128, 255)),
                     # ('lightcyan', (224, 255, 255, 255)),
                     # # ('lightcyan1', (224, 255, 255, 255)),
                     # # ('lightcyan2', (209, 238, 238, 255)),
                     # # ('lightcyan3', (180, 205, 205, 255)),
                     # # ('lightcyan4', (122, 139, 139, 255)),
                     # ('lightgoldenrod', (238, 221, 130, 255)),
                     # # ('lightgoldenrod1', (255, 236, 139, 255)),
                     # # ('lightgoldenrod2', (238, 220, 130, 255)),
                     # # ('lightgoldenrod3', (205, 190, 112, 255)),
                     # # ('lightgoldenrod4', (139, 129, 76, 255)),
                     # ('lightgoldenrodyellow', (250, 250, 210, 255)),
                     # ('lightgreen', (144, 238, 144, 255)),
                     # ('lightpink', (255, 182, 193, 255)),
                     # # ('lightpink1', (255, 174, 185, 255)),
                     # # ('lightpink2', (238, 162, 173, 255)),
                     # # ('lightpink3', (205, 140, 149, 255)),
                     # # ('lightpink4', (139, 95, 101, 255)),
                     # ('lightsalmon', (255, 160, 122, 255)),
                     # # ('lightsalmon1', (255, 160, 122, 255)),
                     # # ('lightsalmon2', (238, 149, 114, 255)),
                     # # ('lightsalmon3', (205, 129, 98, 255)),
                     # # ('lightsalmon4', (139, 87, 66, 255)),
                     # ('lightseagreen', (32, 178, 170, 255)),
                     # ('lightskyblue', (135, 206, 250, 255)),
                     # # ('lightskyblue1', (176, 226, 255, 255)),
                     # # ('lightskyblue2', (164, 211, 238, 255)),
                     # # ('lightskyblue3', (141, 182, 205, 255)),
                     # # ('lightskyblue4', (96, 123, 139, 255)),
                     # ('lightslateblue', (132, 112, 255, 255)),
                     # ('lightsteelblue', (176, 196, 222, 255)),
                     # # ('lightsteelblue1', (202, 225, 255, 255)),
                     # # ('lightsteelblue2', (188, 210, 238, 255)),
                     # # ('lightsteelblue3', (162, 181, 205, 255)),
                     # # ('lightsteelblue4', (110, 123, 139, 255)),
                     # ('lightyellow', (255, 255, 224, 255)),
                     # # ('lightyellow1', (255, 255, 224, 255)),
                     # # ('lightyellow2', (238, 238, 209, 255)),
                     # # ('lightyellow3', (205, 205, 180, 255)),
                     # # ('lightyellow4', (139, 139, 122, 255)),
                     ('limegreen', (50, 205, 50, 255)),
                     ('linen', (250, 240, 230, 255)),
                     ('magenta', (255, 0, 255, 255)),
                     # ('magenta1', (255, 0, 255, 255)),
                     # ('magenta2', (238, 0, 238, 255)),
                     # ('magenta3', (205, 0, 205, 255)),
                     # ('magenta4', (139, 0, 139, 255)),
                     ('maroon', (176, 48, 96, 255)),
                     # ('maroon1', (255, 52, 179, 255)),
                     # ('maroon2', (238, 48, 167, 255)),
                     # ('maroon3', (205, 41, 144, 255)),
                     # ('maroon4', (139, 28, 98, 255)),
                     ('mediumaquamarine', (102, 205, 170, 255)),
                     ('mediumblue', (0, 0, 205, 255)),
                     ('mediumorchid', (186, 85, 211, 255)),
                     # ('mediumorchid1', (224, 102, 255, 255)),
                     # ('mediumorchid2', (209, 95, 238, 255)),
                     # ('mediumorchid3', (180, 82, 205, 255)),
                     # ('mediumorchid4', (122, 55, 139, 255)),
                     ('mediumpurple', (147, 112, 219, 255)),
                     # ('mediumpurple1', (171, 130, 255, 255)),
                     # ('mediumpurple2', (159, 121, 238, 255)),
                     # ('mediumpurple3', (137, 104, 205, 255)),
                     # ('mediumpurple4', (93, 71, 139, 255)),
                     ('mediumseagreen', (60, 179, 113, 255)),
                     ('mediumslateblue', (123, 104, 238, 255)),
                     ('mediumspringgreen', (0, 250, 154, 255)),
                     ('mediumturquoise', (72, 209, 204, 255)),
                     ('mediumvioletred', (199, 21, 133, 255)),
                     ('midnightblue', (25, 25, 112, 255)),
                     ('mintcream', (245, 255, 250, 255)),
                     ('mistyrose', (255, 228, 225, 255)),
                     # ('mistyrose1', (255, 228, 225, 255)),
                     # ('mistyrose2', (238, 213, 210, 255)),
                     # ('mistyrose3', (205, 183, 181, 255)),
                     # ('mistyrose4', (139, 125, 123, 255)),
                     ('moccasin', (255, 228, 181, 255)),
                     ('navy', (0, 0, 128, 255)),
                     ('navyblue', (0, 0, 128, 255)),
                     ('oldlace', (253, 245, 230, 255)),
                     ('olivedrab', (107, 142, 35, 255)),
                     # ('olivedrab1', (192, 255, 62, 255)),
                     # ('olivedrab2', (179, 238, 58, 255)),
                     # ('olivedrab3', (154, 205, 50, 255)),
                     # ('olivedrab4', (105, 139, 34, 255)),
                     ('orange', (255, 165, 0, 255)),
                     # ('orange1', (255, 165, 0, 255)),
                     # ('orange2', (238, 154, 0, 255)),
                     # ('orange3', (205, 133, 0, 255)),
                     # ('orange4', (139, 90, 0, 255)),
                     ('orangered', (255, 69, 0, 255)),
                     # ('orangered1', (255, 69, 0, 255)),
                     # ('orangered2', (238, 64, 0, 255)),
                     # ('orangered3', (205, 55, 0, 255)),
                     # ('orangered4', (139, 37, 0, 255)),
                     ('orchid', (218, 112, 214, 255)),
                     # ('orchid1', (255, 131, 250, 255)),
                     # ('orchid2', (238, 122, 233, 255)),
                     # ('orchid3', (205, 105, 201, 255)),
                     # ('orchid4', (139, 71, 137, 255)),
                     ('palegoldenrod', (238, 232, 170, 255)),
                     ('palegreen', (152, 251, 152, 255)),
                     # ('palegreen1', (154, 255, 154, 255)),
                     # ('palegreen2', (144, 238, 144, 255)),
                     # ('palegreen3', (124, 205, 124, 255)),
                     # ('palegreen4', (84, 139, 84, 255)),
                     ('paleturquoise', (175, 238, 238, 255)),
                     # ('paleturquoise1', (187, 255, 255, 255)),
                     # ('paleturquoise2', (174, 238, 238, 255)),
                     # ('paleturquoise3', (150, 205, 205, 255)),
                     # ('paleturquoise4', (102, 139, 139, 255)),
                     ('palevioletred', (219, 112, 147, 255)),
                     # ('palevioletred1', (255, 130, 171, 255)),
                     # ('palevioletred2', (238, 121, 159, 255)),
                     # ('palevioletred3', (205, 104, 137, 255)),
                     # ('palevioletred4', (139, 71, 93, 255)),
                     ('papayawhip', (255, 239, 213, 255)),
                     ('peachpuff', (255, 218, 185, 255)),
                     # ('peachpuff1', (255, 218, 185, 255)),
                     # ('peachpuff2', (238, 203, 173, 255)),
                     # ('peachpuff3', (205, 175, 149, 255)),
                     # ('peachpuff4', (139, 119, 101, 255)),
                     ('peru', (205, 133, 63, 255)),
                     ('pink', (255, 192, 203, 255)),
                     # ('pink1', (255, 181, 197, 255)),
                     # ('pink2', (238, 169, 184, 255)),
                     # ('pink3', (205, 145, 158, 255)),
                     # ('pink4', (139, 99, 108, 255)),
                     ('plum', (221, 160, 221, 255)),
                     # ('plum1', (255, 187, 255, 255)),
                     # ('plum2', (238, 174, 238, 255)),
                     # ('plum3', (205, 150, 205, 255)),
                     # ('plum4', (139, 102, 139, 255)),
                     ('powderblue', (176, 224, 230, 255)),
                     ('purple', (160, 32, 240, 255)),
                     # ('purple1', (155, 48, 255, 255)),
                     # ('purple2', (145, 44, 238, 255)),
                     # ('purple3', (125, 38, 205, 255)),
                     # ('purple4', (85, 26, 139, 255)),
                     ('red', (255, 0, 0, 255)),
                     # ('red1', (255, 0, 0, 255)),
                     # ('red2', (238, 0, 0, 255)),
                     # ('red3', (205, 0, 0, 255)),
                     # ('red4', (139, 0, 0, 255)),
                     ('rosybrown', (188, 143, 143, 255)),
                     # ('rosybrown1', (255, 193, 193, 255)),
                     # ('rosybrown2', (238, 180, 180, 255)),
                     # ('rosybrown3', (205, 155, 155, 255)),
                     # ('rosybrown4', (139, 105, 105, 255)),
                     ('royalblue', (65, 105, 225, 255)),
                     # ('royalblue1', (72, 118, 255, 255)),
                     # ('royalblue2', (67, 110, 238, 255)),
                     # ('royalblue3', (58, 95, 205, 255)),
                     # ('royalblue4', (39, 64, 139, 255)),
                     ('saddlebrown', (139, 69, 19, 255)),
                     ('salmon', (250, 128, 114, 255)),
                     # ('salmon1', (255, 140, 105, 255)),
                     # ('salmon2', (238, 130, 98, 255)),
                     # ('salmon3', (205, 112, 84, 255)),
                     # ('salmon4', (139, 76, 57, 255)),
                     ('sandybrown', (244, 164, 96, 255)),
                     ('seagreen', (46, 139, 87, 255)),
                     # ('seagreen1', (84, 255, 159, 255)),
                     # ('seagreen2', (78, 238, 148, 255)),
                     # ('seagreen3', (67, 205, 128, 255)),
                     # ('seagreen4', (46, 139, 87, 255)),
                     ('seashell', (255, 245, 238, 255)),
                     # ('seashell1', (255, 245, 238, 255)),
                     # ('seashell2', (238, 229, 222, 255)),
                     # ('seashell3', (205, 197, 191, 255)),
                     # ('seashell4', (139, 134, 130, 255)),
                     ('sienna', (160, 82, 45, 255)),
                     # ('sienna1', (255, 130, 71, 255)),
                     # ('sienna2', (238, 121, 66, 255)),
                     # ('sienna3', (205, 104, 57, 255)),
                     # ('sienna4', (139, 71, 38, 255)),
                     ('skyblue', (135, 206, 235, 255)),
                     # ('skyblue1', (135, 206, 255, 255)),
                     # ('skyblue2', (126, 192, 238, 255)),
                     # ('skyblue3', (108, 166, 205, 255)),
                     # ('skyblue4', (74, 112, 139, 255)),
                     ('slateblue', (106, 90, 205, 255)),
                     # ('slateblue1', (131, 111, 255, 255)),
                     # ('slateblue2', (122, 103, 238, 255)),
                     # ('slateblue3', (105, 89, 205, 255)),
                     # ('slateblue4', (71, 60, 139, 255)),
                     ('snow', (255, 250, 250, 255)),
                     # ('snow1', (255, 250, 250, 255)),
                     # ('snow2', (238, 233, 233, 255)),
                     # ('snow3', (205, 201, 201, 255)),
                     # ('snow4', (139, 137, 137, 255)),
                     ('springgreen', (0, 255, 127, 255)),
                     # ('springgreen1', (0, 255, 127, 255)),
                     # ('springgreen2', (0, 238, 118, 255)),
                     # ('springgreen3', (0, 205, 102, 255)),
                     # ('springgreen4', (0, 139, 69, 255)),
                     ('steelblue', (70, 130, 180, 255)),
                     # ('steelblue1', (99, 184, 255, 255)),
                     # ('steelblue2', (92, 172, 238, 255)),
                     # ('steelblue3', (79, 148, 205, 255)),
                     # ('steelblue4', (54, 100, 139, 255)),
                     ('tan', (210, 180, 140, 255)),
                     # ('tan1', (255, 165, 79, 255)),
                     # ('tan2', (238, 154, 73, 255)),
                     # ('tan3', (205, 133, 63, 255)),
                     # ('tan4', (139, 90, 43, 255)),
                     ('thistle', (216, 191, 216, 255)),
                     # ('thistle1', (255, 225, 255, 255)),
                     # ('thistle2', (238, 210, 238, 255)),
                     # ('thistle3', (205, 181, 205, 255)),
                     # ('thistle4', (139, 123, 139, 255)),
                     ('tomato', (255, 99, 71, 255)),
                     # ('tomato1', (255, 99, 71, 255)),
                     # ('tomato2', (238, 92, 66, 255)),
                     # ('tomato3', (205, 79, 57, 255)),
                     # ('tomato4', (139, 54, 38, 255)),
                     ('turquoise', (64, 224, 208, 255)),
                     # ('turquoise1', (0, 245, 255, 255)),
                     # ('turquoise2', (0, 229, 238, 255)),
                     # ('turquoise3', (0, 197, 205, 255)),
                     # ('turquoise4', (0, 134, 139, 255)),
                     ('violet', (238, 130, 238, 255)),
                     ('violetred', (208, 32, 144, 255)),
                     # ('violetred1', (255, 62, 150, 255)),
                     # ('violetred2', (238, 58, 140, 255)),
                     # ('violetred3', (205, 50, 120, 255)),
                     # ('violetred4', (139, 34, 82, 255)),
                     ('wheat', (245, 222, 179, 255)),
                     # ('wheat1', (255, 231, 186, 255)),
                     # ('wheat2', (238, 216, 174, 255)),
                     # ('wheat3', (205, 186, 150, 255)),
                     # ('wheat4', (139, 126, 102, 255)),
                     ('yellow', (255, 255, 0, 255)),
                     # ('yellow1', (255, 255, 0, 255)),
                     # ('yellow2', (238, 238, 0, 255)),
                     # ('yellow3', (205, 205, 0, 255)),
                     # ('yellow4', (139, 139, 0, 255)),
                     ('yellowgreen', (154, 205, 50, 255))]
__colors = __original_colors.copy()
random.shuffle(__colors)


def get_color():
    global __colors
    if len(__colors) > 0:
        return __colors.pop()
    else:
        __colors = __original_colors.copy()
        random.shuffle(__colors)
        return __colors.pop()
