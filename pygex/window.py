from pygame.display import set_mode as pg_win_set_mode, set_caption as pg_win_set_caption, flip as pg_display_flip
from pygame.display import get_surface as pg_win_get_surface, get_window_size as pg_win_get_size
from pygame.display import get_caption as pg_win_get_caption, init as pg_display_init
from pygame.display import get_desktop_sizes as pg_get_desktop_sizes
from pygame.constants import QUIT, FULLSCREEN, RESIZABLE
from pygame.image import save as pg_save_image
from pygame.time import Clock as pg_Clock
from pygex.input import get_input, Input
from pygex.mouse import get_mouse, Mouse
from pygex.color import colorValue
from pygame.event import Event
from datetime import datetime
from typing import Sequence
from os.path import isdir
from os import makedirs
from time import time


class Window:
    def __init__(self, size: Sequence = (800, 600), title='Pygex window', vsync=False, flags=0):
        global _active_window
        _active_window = self

        pg_display_init()

        pg_win_set_mode(size, flags | RESIZABLE, vsync=vsync)
        pg_win_set_caption(title)

        if get_mouse() is None:
            Mouse()

        if get_input() is None:
            Input()

        self._clock = pg_Clock()
        self._fps_counter_start_time = time()
        self._fps_counter_num = 0
        self._fps_num = 60

        self._size = *size,
        self._vsync = vsync

        self.default_quit = True
        self.fps_limit: float | None = None
        self.bg_color: colorValue | None = None

    @property
    def title(self):
        return pg_win_get_caption()[0]

    @title.setter
    def title(self, value: str):
        pg_win_set_caption(value)

    @property
    def size(self):
        return pg_win_get_size() if not self.fullscreen else pg_get_desktop_sizes()[0]

    @size.setter
    def size(self, value: Sequence):
        if not self.fullscreen:
            self._size = *value,
            pg_win_set_mode(value, pg_win_get_surface().get_flags(), vsync=self._vsync)

    @property
    def mouse(self):
        return get_mouse()

    @property
    def input(self):
        return get_input()

    @property
    def clock(self):
        return self._clock

    @property
    def surface(self):
        return pg_win_get_surface()

    @property
    def fps(self):
        return self._fps_num if self.fps_limit is None else self._clock.get_fps()

    @property
    def flags(self):
        return pg_win_get_surface().get_flags()

    @flags.setter
    def flags(self, value: int):
        pg_win_set_mode(pg_win_get_size(), value, vsync=self._vsync)

    @property
    def fullscreen(self):
        return bool(pg_win_get_surface().get_flags() & FULLSCREEN)

    @fullscreen.setter
    def fullscreen(self, value: bool):
        if not self.fullscreen and self.resizable:
            self._size = pg_win_get_size()

        new_size = pg_get_desktop_sizes()[0] if value and not self.fullscreen else self._size

        pg_win_set_mode(new_size, (self.flags | FULLSCREEN) if value else (self.flags & ~FULLSCREEN), vsync=self._vsync)

    @property
    def resizable(self):
        return bool(pg_win_get_surface().get_flags() & RESIZABLE)

    @resizable.setter
    def resizable(self, value: bool):
        self.flags = (self.flags | RESIZABLE) if value else (self.flags & ~RESIZABLE)

    def add_flags(self, flags: int):
        self.flags |= flags

    def remove_flags(self, flags: int):
        self.flags &= ~flags

    def take_screenshot(self, save_directory='./screenshots'):
        if not isdir(save_directory):
            makedirs(save_directory)

        pg_save_image(
            pg_win_get_surface(),
            save_directory + '/' +
            f'screenshot_{datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f")}_{self.title.lower().replace(" ", "_")}.png'
        )

    def process_event(self, e: Event):
        if self.default_quit and e.type == QUIT:
            exit()

        get_mouse().process_event(e)
        get_input().process_event(e)

    def flip(self):
        pg_display_flip()
        get_mouse().flip()
        get_input().flip()

        self._fps_counter_num += 1

        if time() - self._fps_counter_start_time >= 1:
            self._fps_counter_start_time = time()
            self._fps_num = self._fps_counter_num
            self._fps_counter_num = 0

        if self.bg_color is not None:
            pg_win_get_surface().fill(self.bg_color)

        if self.fps_limit is not None:
            self._clock.tick(self.fps_limit)


_active_window: Window | None = None


def get_window():
    return _active_window


__all__ = 'Window', 'get_window'