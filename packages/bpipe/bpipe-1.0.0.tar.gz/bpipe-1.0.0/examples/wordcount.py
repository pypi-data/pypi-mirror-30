#!/usr/bin/env python3
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
import re
from bpipe import pipe

S1 = "I scream,"
S2 = "You scream,"
S3 = "They scream,"
S4 = "We all scream for an ice cream!"

p = pipe([S1, S2, S3, S4], debug=False) \
    .map(lambda t: re.sub("[^0-9a-zA-Z]+", " ", t)) \
    .map(lambda t: t.lower()) \
    .map(lambda t: t.split()) \
    .flatten() \
    .group_by()

for w, c in p:
    print(w, c)
