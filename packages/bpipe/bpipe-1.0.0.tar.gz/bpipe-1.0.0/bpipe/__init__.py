# -*- coding: utf-8 -*-
# bpipe - Minimal & Simple Pipeline for Python
#
# Copyright (C) 2017-present Jeremies Pérez Morata
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
bpipe : Minimal & Simple Pipeline for Python
~~~~

Example:
```
from bpipe import *

for r in echo("Hello World") | map_to(lambda x: x.upper()):
    print(r)

# HELLO WORLD
```
"""

from os import path as p
from builtins import *  # noqa # pylint: disable=unused-import
from bpipe.pipe import Pipe
from bpipe.sources import cat, echo, map_to, flatten, flat_map, curl

__version__ = '1.0.0'

__title__ = 'bpipe'
__package_name__ = 'bpipe'
__author__ = 'Jeremies Perez'
__description__ = 'Minimal & Simple Pipeline for Python'
__email__ = 'jeremiespm@gmail.com'
__license__ = 'GPL v3'
__copyright__ = 'Copyright 2017-now Jeremies Perez Morata'

PARENT_DIR = p.abspath(p.dirname(__file__))
ENCODING = 'utf-8'


def get_path(name):
    return 'file://%s' % p.join(PARENT_DIR, 'data', name)


def pipe(*args, **kwargs):
    return Pipe(*args, **kwargs)

__all__ = ['cat', 'echo', 'map_to', 'pipe', 'flatten', 'flat_map', 'curl']
