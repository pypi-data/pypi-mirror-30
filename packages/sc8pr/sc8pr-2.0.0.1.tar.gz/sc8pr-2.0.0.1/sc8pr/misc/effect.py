# Copyright 2015-2018 D.G. MacCarthy <http://dmaccarthy.github.io>
#
# This file is part of "sc8pr".
#
# "sc8pr" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "sc8pr" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "sc8pr".  If not, see <http://www.gnu.org/licenses/>.


from random import uniform, random
from math import sqrt, tan, pi
import pygame
from pygame.pixelarray import PixelArray
from sc8pr.util import rgba, style

pi2 = 2 * pi


class Effect:
    "Base class for all effects / transitions"
    _time = None

    def time(self, fullEffect, noEffect):
        self._time = fullEffect, noEffect
        return self

    def transition(self, img, n):
        if self._time is None: n = 0
        else:
            t0, t1 = self._time
            n = (n - t0) / (t1 - t0)
        return self.apply(img, 0 if n <= 0 else 1 if n >= 1 else n)

    def srfSize(self, img, size=False):
        srf = img if isinstance(img, pygame.Surface) else img.image
        return (srf, srf.get_size()) if size else srf


class ReplaceColor(Effect):
    "Replace one color by another (non-animated)"

    def __init__(self, color, replace=(0,0,0,0), dist=0):
        self.color1 = rgba(color)
        self.color2 = rgba(replace)
        self.dist = dist

    def apply(self, img, n=0):
        srf = self.srfSize(img)
        d = self.dist * (1 - n)
        pygame.PixelArray(srf).replace(self.color1, self.color2, d)
        return img


class Style(Effect):
    "Add a border or background (non-animated)"
    
    def __init__(self, **kwargs):
        if "padding" in kwargs: # Alters blit rect!
            raise NotImplementedError("Keyword 'padding' is not permitted")
        self.kwargs = kwargs
    
    def apply(self, img, n=0):
        return style(img, **self.kwargs)


class Tint(Effect):
    "Adjust the color and/or transparency"

    def __init__(self, color=(255,255,255,0)):
        self.color = rgba(color)

    def apply(self, img, n=0):
        if n < 1:
            srf = self.srfSize(img)
            color = [round(c + (255 - c) * n) for c in self.color]
            srf.fill(color, None, pygame.BLEND_RGBA_MULT)
        return img


class Wipe(Effect):
    "Wipe in or out from any corner, side, or center"

    def __init__(self, start=5): self.start = start

    @staticmethod
    def _dim(n, start, w0):
        "Calculate 'wiped' position and size in one dimension"
        if start is not None:
            w = round(n * w0)
            dw = w0 - w
            x = dw//2 if start & 1 else dw if start & 2 else 0
            return x, w
        return 0, w0

    @staticmethod
    def _apply(srf, pos, size, origSize):
        "Blit the visible subsurface onto a transparent background"
        img = pygame.Surface(origSize, pygame.SRCALPHA)
        img.blit(srf.subsurface(pos, size), pos)
        return img

    def apply(self, img, n=0):
        srf, sz = self.srfSize(img, True)
        s = self.start
        wx = None if s in (1, 9) else (s & 3)
        wy = None if s in (4, 6) else (s >> 2)
        x, w = self._dim(n, wx, sz[0])
        y, h = self._dim(n, wy, sz[1])
        return self._apply(srf, (x,y), (w,h), sz)


class Squash(Wipe):

    @staticmethod
    def _apply(srf, pos, size, origSize):
        "Blit the scaled image onto a transparent background"
        srf = pygame.transform.smoothscale(srf, size)
        img = pygame.Surface(origSize, pygame.SRCALPHA)
        img.blit(srf, pos)
        return img


class MathEffect(Effect):
    "Effect based on y < f(x) or y > f(x)"

    def __init__(self, eqn=None, noise=0.15, fill=(0,0,0,0)):
        self.fill = rgba(fill)
        self.dh = noise
        if eqn: self.eqn = eqn.__get__(self, self.__class__)

    def eqn(self, x, n, size):
        dh = self.dh
        return size[1] * ((1 + dh) * n - uniform(0, dh)), True

    def apply(self, img, n=0):
        "Modify image based on equation provided"
        srf, size = self.srfSize(img, True)
        h = size[1]
        pxa = PixelArray(srf)
        x = 0
        for pxCol in pxa:
            y = self.eqn(x, n, size)
            if type(y) is tuple: y, above = y
            else: above = True
            if type(y) is float: y = int(y)
            if above:
                if y < h - 1:
                    if y < 0: y = 0
                    pxCol[y:] = self.fill
            elif y > 0:
                if y > h: y = h
                pxCol[:y] = self.fill
            x += 1
        return srf


class WipeSlope(MathEffect):
    "Wipe diagonally from any corner"

    def __init__(self, slope=False, above=True, fill=(0,0,0,0)):
        self.slope = slope
        self.above = above
        self.fill = rgba(fill)

    def eqn(self, x, n, size):
        w, h = size
        k = self.slope
        if type(k) is bool:
            k = h / w * (1 if k else -1)
        if not self.above: n = 1 - n
        dy = k * w
        if k < 0: b = n * (h - dy)
        else: b = n * (h + dy) - dy
        return k * x + b, self.above


class PaintDrops(MathEffect):

    def __init__(self, drops=64, fill=(0,0,0,0)):
        self.fill = rgba(fill)
        self.side = drops > 0
        self.drops = [self.makeDrop() for i in range(abs(drops))]
        n = sum([d[0] for d in self.drops])
        for d in self.drops: d[0] /= n

    def eqn(self, x, n, size):
        "Calculate paint boundary"
        if not self.side: n = 1 - n
        w, h = size
        y = 0
        xc = 0
        for d in self.drops:
            r = d[0] * w / 2
            R = 1.1 * r
            xc += r
            dx = abs(x - xc)
            if dx <= R:
                dy = sqrt(R * R - dx * dx)
                Y = (h + R) * self.posn(n, *d[1:]) + dy - R
                if Y > y: y = Y
            xc += r
        return y, self.side

    def posn(self, n, t1, t2):
        "Calculate drop position"
        if n < t1: return 0
        elif n > t2: return 1
        return (n - t1) / (t2 - t1)

    @staticmethod
    def makeDrop():
        "Create random diameter, start and end time"
        t1 = uniform(0, 0.8)
        t2 = uniform(t1 + 0.1, 1)
        return [uniform(0.1, 1), min(t1, t2), max(t1, t2)]


class Dissolve(Effect):
    "Replace pixels randomly by a specified or random color"

    def __init__(self, colors=(0,0,0,0), alpha=True, keepTransparent=True):
        if not colors: self.colors = alpha
        elif type(colors) is int:
            self.colors = [rgba(alpha) for i in range(colors)]
        else:
            if type(colors) in (str, pygame.Color) or type(colors[0]) is int:
                colors = colors,
            self.colors = [rgba(i) for i in colors]
        self.n = -1
        self.keep = keepTransparent

    def apply(self, img, n):
        "Apply pixel-by-pixel effect"
        srf = self.srfSize(img)
        self.alphaMask = srf.map_rgb((0,0,0,255))
        pxa = PixelArray(srf)
        x = 0
        for pxCol in pxa:
            for y in range(len(pxCol)):
                pxCol[y] = self.pixel(n, x, y, pxCol[y])
            x += 1
        return srf

    def pixel(self, n, x, y, c):
        "Calculate pixel color"
        if random() <= n or (self.keep and c & self.alphaMask == 0):
            return c
        c = self.colors
        if type(c) is bool: return rgba(c)
        self.n = (self.n + 1) % len(self.colors)
        return c[self.n]


class ClockHand(MathEffect):

    def __init__(self, clockwise=True, fill=(0,0,0,0)):
        self.fill = rgba(fill)
        self.cw = clockwise

    def eqn(self, x, n, size):
        if n <= 0: return 0
        h = size[1]
        y = h / 2
        x -= size[0] / 2
        if not self.cw: x = -x
        if x < 0:
            return 0 if n <= 0.5 else (y + x * tan((n - 0.75) * pi2), False)
        else:
            return h if n >= 0.5 else (y + x * tan((n - 0.25) * pi2))
