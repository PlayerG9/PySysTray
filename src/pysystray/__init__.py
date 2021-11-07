# coding=utf-8
r"""
pystray
Copyright (C) 2021 PlayerG9

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import sys

from ._info import __author__, __version__


if sys.platform == 'win32':  # Windows
    from ._win32 import Icon
elif sys.platform == 'linux':  # Linux/Ubuntu
    try:
        from ._gtk import Icon
    except Exception:
        raise ImportError('this platform is not supported')
# elif sys.platform == 'darwin':  # macOs
#     from ._darwin import Icon
else:
    raise ImportError('this platform is not supported')
