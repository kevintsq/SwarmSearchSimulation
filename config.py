import sys

from pygame import Color

MAX_ITER = 100
PAUSE = False
DARK_MODE = True

if DARK_MODE:
    FOREGROUND_COLOR = Color("white")
    BACKGROUND_COLOR = Color("black")
    VISITED_COLOR = Color(39, 130, 215)  # dark blue
    RESCUED_COLOR = Color(26, 173, 25)  # dark green
    FAILED_RESCUE_COLOR = Color(216, 78, 67)  # dark red
else:
    FOREGROUND_COLOR = Color("black")
    BACKGROUND_COLOR = Color("white")
    VISITED_COLOR = Color(16, 174, 255)  # light blue
    RESCUED_COLOR = Color(145, 237, 97)  # light green
    FAILED_RESCUE_COLOR = Color(247, 98, 96)  # light red

FAILED_VISIT_COLOR = Color(255, 190, 0)  # Orange

SCALING_FACTOR = 1
DISPLAY_FREQUENCY = 60

if sys.platform == 'win32':
    import ctypes
    import win32api

    DISPLAY_FREQUENCY = win32api.EnumDisplaySettings().DisplayFrequency
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # if your Windows version >= 8.1
        # monitors = win32api.EnumDisplayMonitors()
        # scaling_factor = ctypes.c_int()
        # ctypes.windll.shcore.GetScaleFactorForMonitor(monitors[0][0].handle, ctypes.byref(scaling_factor))
        # SCALING_FACTOR = scaling_factor.value // 100
    except:
        ctypes.windll.user32.SetProcessDPIAware()  # Windows 8 or less
    dpi = ctypes.windll.user32.GetDpiForSystem()
    SCALING_FACTOR = dpi / 96
    SCALING_FACTOR /= 1.5
