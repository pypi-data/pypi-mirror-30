#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Pybeeryaml
# Copyright (C) 2018  TROUVERIE Joachim <joachim.trouverie@linoame.fr>
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


from pybeeryaml.meta import BeerComponent


class Style(BeerComponent):

    def __init__(self, name, category, category_number, style_letter,
                 style_guide, type, og_min, og_max, fg_min, fg_max, ibu_min,
                 ibu_max, color_min, color_max, **kwargs):
        super().__init__()

        self.name = name
        self.category = category
        self.category_number = category_number
        self.style_letter = style_letter
        self.style_guide = style_guide
        self.type = type
        self.og_min = og_min
        self.og_max = og_max
        self.fg_min = fg_min
        self.fg_max = fg_max
        self.ibu_min = ibu_min
        self.ibu_max = ibu_max
        self.color_min = color_min
        self.color_max = color_max

        self.set(kwargs)
