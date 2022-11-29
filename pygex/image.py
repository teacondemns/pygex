from pygame.image import frombuffer as pg_image_frombuffer, tostring as pg_image_tostring
from PIL import Image as PillowImage, ImageFilter as PillowImageFilter
from pygame.transform import smoothscale as pg_smoothscale
from pygex.color import colorValue, to_pygame_alpha_color
from pygame.surface import Surface, SurfaceType
from pygame.draw import rect as pg_draw_rect
from pygame.constants import SRCALPHA
from typing import Sequence


def AlphaSurface(size: Sequence, flags: int = 0):
    return Surface(size, flags | SRCALPHA, 32)


def pillow_to_pygame(source_surface: PillowImage):
    return pg_image_frombuffer(source_surface.tobytes(), source_surface.size, 'RGBA')


def pygame_to_pillow(source_surface: SurfaceType):
    return PillowImage.frombytes('RGBA', source_surface.get_size(), pg_image_tostring(source_surface, 'RGBA'))


def blur(source_surface: SurfaceType, radius: int):
    return pillow_to_pygame(pygame_to_pillow(source_surface).filter(PillowImageFilter.GaussianBlur(radius)))


def cutout_by_mask(source_surface: SurfaceType, mask: SurfaceType):
    """
    The cutout color on the mask is black (#000000)
    :param source_surface: original Surface
    :param mask: mask for cutout
    """
    new_source = source_surface.copy()

    for x in range(0, source_surface.get_size()[0]):
        for y in range(0, source_surface.get_size()[1]):
            if mask.get_at((x, y)) == (0, 0, 0, 255):
                new_source.set_at((x, y), 0x00000000)

    return new_source


def round_corners(source_surface: SurfaceType, radius: int | tuple[int, int, int, int] | Sequence):
    """
    Rounding the borders of image (Surface)
    :param source_surface: source_surface image
    :param radius: value by which the corners will be rounded: `radius` or `top_left, top_right, bottom_left, bottom_tight`
    """
    radius = (radius,) if isinstance(radius, int) else (-1, *radius)
    mask_surface = Surface(source_surface.get_size())
    mask_surface.fill(0x000000)

    pg_draw_rect(mask_surface, 0xffffff, (0, 0, *source_surface.get_size()), 0, *radius)

    return cutout_by_mask(source_surface, mask_surface)


def gradient(size: Sequence, colors: Sequence[colorValue], is_vertical=False):
    colors_line_surface = Surface((1, len(colors)) if is_vertical else (len(colors), 1), SRCALPHA, 32)

    for i in range(len(colors)):
        colors_line_surface.set_at((0, i) if is_vertical else (i, 0), to_pygame_alpha_color(colors[i]))

    return pg_smoothscale(colors_line_surface, size)


__all__ = 'AlphaSurface', 'pillow_to_pygame', 'pygame_to_pillow', 'blur', 'cutout_by_mask', 'round_corners', 'gradient'
