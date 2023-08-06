#!/usr/bin/env python3
#
# This file is part of Script of Scripts (sos), a workflow system
# for the execution of commands and scripts in different languages.
# Please visit https://github.com/vatlab/SOS for more information.
#
# Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import pydoc
from sos.utils import env
from sos.syntax import SOS_USAGES

class SoS_VariableInspector(object):
    def __init__(self, kernel):
        self.kernel = kernel

    def inspect(self, name, line, pos):
        try:
            obj_desc, preview = self.kernel.preview_var(name, style=None)
            if preview is None:
                return {}
            else:
                format_dict, md_dict = preview
                if 'text/plain' in format_dict:
                    return format_dict
                else:
                    return {'text/plain': f'{repr(env.sos_dict["name"])} ({obj_desc})'}
        except Exception:
            return {}

class SoS_SyntaxInspector(object):
    def __init__(self, kernel):
        self.kernel = kernel

    def inspect(self, name, line, pos):
        if line.startswith('%') and name in self.kernel.ALL_MAGICS and pos <= len(name) + 1:
            if hasattr(self.kernel, f'get_{name}_parser'):
                parser = getattr(self.kernel, f'get_{name}_parser')()
                return {'text/plain': parser.format_help()}
            else:
                return {'text/plain': f'Magic %{name}'}
        elif line.startswith(name + ':') and pos <= len(name):
            if self.kernel.original_keys is None:
                self.kernel._reset_dict()
            # input: etc
            if name in SOS_USAGES:
                return {'text/plain': SOS_USAGES[name]}
            elif name in env.sos_dict:
                # action?
                return {'text/plain': pydoc.render_doc(env.sos_dict[name], title='%s', renderer=pydoc.plaintext),
                        'text/html': pydoc.render_doc(env.sos_dict[name], title='%s', renderer=pydoc.html)
                        }
            else:
                return {}
        else:
            return {}

class SoS_Inspector(object):
    def __init__(self, kernel):
        self.inspectors = [
            SoS_SyntaxInspector(kernel),
            SoS_VariableInspector(kernel),
        ]

    def inspect(self, name, line, pos):
        for c in self.inspectors:
            try:
                data = c.inspect(name, line, pos)
                if data:
                    return data
            except Exception:
                continue
        # No match
        return {}

