"""
common.py  ver. 0.2.3

(C) Conrad Heidebrecht (github.com/eternali) 16 Mar 2018

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

from colors import Color, Tmode
from os import popen


class CommonColors():
    """List of common colors for easy import.
    Not an explicit enum simply for ease of use (CommonColors.RED instead of CommonColors.RED.value).
    """
    RED = Color('ff0000')
    GREEN = Color('00ff00')
    BLUE = Color('0000ff')
    BLACK = Color('000000')
    WHITE = Color('ffffff')
    RT = Color('000000').rt


def rainbow(cols=0, printchar=' ', mode=Tmode.bg):
    cols = cols or int(popen('tput cols').read().strip())
    rb = ''
    for c in range(cols):
        r = int(255 - (c * 255 / cols))
        g = int(c * 510 / cols)
        b = int(c * 255 / cols)
        if g > 255:
            g = 510 - g

        color = Color((r, g, b))
        if mode.name == 'fg':
            rb += color.fg + printchar
        elif mode.name == 'bg':
            rb += color.bg + printchar

    return rb + CommonColors.RT

