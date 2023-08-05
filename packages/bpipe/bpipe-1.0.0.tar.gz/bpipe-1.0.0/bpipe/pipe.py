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
from bpipe.utils import is_iterable

class Pipe:
    def __init__(self, generator, debug=False, final=False, name=None):
        self.generator = generator
        self.steps = []
        self.error_callback = None
        self.abort_on_error = False
        self.iterator = None
        self.debug = debug
        self.final = final
        self.name = name
        self.results = []

    def peek(self):
        """Observe streaming objects (For development)"""
        def _peek(x):
            print(x)
            return x

        self.steps.append(_peek)
        return self

    def map(self, step):
        """Add transformation to the pipeline"""
        self.steps.append(step)
        return self

    def error(self, error_callback, abort_on_error=False):
        """Handle pipeline errors"""
        self.error_callback = error_callback
        self.abort_on_error = abort_on_error
        return self

    def flatten(self):
        """Unbox boxed elements"""
        def _flatten(x):
            if isinstance(x, list):
                for e in x:
                    yield e
            else:
                return x

        self.steps.append(_flatten)
        return self

    def flat_map(self, step):
        """Unbox the elements and apply the transformation"""
        self.flatten()
        self.map(step)
        return self

    def group_by(self):
        results = list(self)
        c = {}
        for r in results:
            if not r in c:
                c[r] = 0
            c[r] += 1
        return [(k, v) for k, v in c.items()]


    def _execute_steps(self, x, current_steps, debug=False, debug_pad=""):
        result = x
        append_to_result = True
        for idx, step in enumerate(current_steps):
            if debug:
                print("{0}[{1}]".format(debug_pad, idx), result, '-->', step)

            if is_iterable(step):
                append_to_result = False
                for e in step(result):
                    self._execute_steps(e, current_steps[idx + 1:],
                                        debug=debug,
                                        debug_pad=debug_pad + " ")
                break
            else:
                result = step(result)

            if debug:
                print("{0} ==>".format(debug_pad), result)

        if append_to_result:
            self.results.append(result)

    def __or__(self, dst):
        self.steps.extend(dst.steps)
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if not self.generator:
            raise StopIteration
            
        if not self.iterator:
            self.iterator = iter(self.generator)

        if len(self.results) > 0:
            return self.results.pop(0)
        else:
            x = next(self.iterator)
            self._execute_steps(x, self.steps, debug=self.debug)
            if len(self.results) > 0:
                return self.results.pop(0)

    def _go(self):
        for x in self.generator:
            self._execute_steps(x, self.steps, debug=self.debug)

    def list(self):
        result = []

        def _get_result(x):
            result.append(x)
            return x

        self.steps.append(_get_result)
        self._go()
        return result
