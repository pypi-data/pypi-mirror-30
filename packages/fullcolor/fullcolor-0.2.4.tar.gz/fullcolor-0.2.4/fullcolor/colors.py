"""
colors.py  ver. 0.2.4

(C) Conrad Heidebrecht (github.com/eternali) 19 Mar 2018

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from __future__ import print_function
from enum import Enum
import sys


class Tmode(Enum):
    """An enum specifying the modes colors can be printed in the terminal.

    Attributes:
        fg (int): number that specifies the color to be in foreground
        bg (int): number that specifies the color to be in background
    """

    fg = 38  # foreground
    bg = 48  # background


class Color():
    """Holds different color values and provides helper methods for conversions and printing to terminal.

    Args:
        value (:str:tuple:list): color value (either RGB or hex code)
        t (str, optional): format string to print to terminal
        rt (str, optional): string that resets color of terminal

    Attributes:
        rgb (tuple): (RED, GREEN, BLUE) tuple color value
        hexd (string): hexidecimal color value (6 digit string)
        t (string): backup terminal string formatter if it is different than default

        *mode.name (int): list of modes to print the color to terminal from Tmode enum
    """

    __slots__ = ['rgb', 'hexd', 't', 'rt', *[mode.name for mode in Tmode]]
    f_rt = '\033[0m'  # full reset

    def __init__(self, value, t='', rt='\033[0m'):
        if type(value) == str:
            self.hexd = self.parse_hexd(value)
            self.rgb = self.calc_rgb(hexd=self.hexd, term=t)
        elif type(value) in [tuple, list] and len(value) == 3:
            self.rgb = tuple(value)
            self.hexd = self.calc_hexd(rgb=self.rgb, term=t)
        
        self.t = t
        self.rt = rt
        for mode in Tmode:
            exec('self.%s = self.calc_term(rgb=self.rgb, hexd=self.hexd, tmode=Tmode.%s)' % (mode.name, mode.name))

    def print(self, mode, text):
        print(mode + text, end=self.rt)

    @staticmethod
    def parse_hexd(hexd):
        hexd = hexd.strip('#')
        if len(hexd) == 3:
            return ''.join([h * 2 for h in hexd])
        elif len(hexd) == 6:
            return hexd
        if not len(hexd) in [3, 6]:
            raise ValueError(str(hexd) + ' is not a valid hex code.')

    @staticmethod
    def calc_hexd(rgb=(), term=''):
        if rgb:
            return ''.join([str(hex(d)) for d in rgb])
        if term:
            return ''
        else:
            raise ValueError('Unable to calculate hexidecimal color value.')

    @classmethod
    def calc_rgb(cls, hexd='', term=''):
        if hexd:
            hexd = cls.parse_hexd(hexd) if len(hexd) != 6 else hexd
            return tuple([int(hexd[i:i+2], 16) for i in range(0, len(hexd), 2)])
        elif term:
            return () 
        else:
            raise ValueError('Unable to calculate RGB color value.')
    
    @classmethod
    def calc_term(cls, rgb=(), hexd='', tmode=Tmode.fg):
        if rgb:
            return '\033[%d;2;%d;%d;%dm' % (tmode.value, *rgb)
        elif hexd:
            hexd = cls.parse_hexd(hexd)
            return '\033[%d;2;%d;%d;%dm' % (tmode.value, *[int(hexd[i:i+2], 16) for i in range(0, len(hexd), 2)])
        else:
            raise ValueError('Unable to calculate terminal compatible color.')

    @staticmethod
    def reset_term(pipe=sys.stdout, rt='\033[0m'):
        pipe.write(rt)
        pipe.flush()

