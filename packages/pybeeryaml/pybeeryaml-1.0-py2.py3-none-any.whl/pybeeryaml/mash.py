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


class MashProfile(BeerComponent):

    def __init__(self, name, grain_temp, **kwargs):
        super().__init__("mash")

        self.name = name
        self.grain_temp = grain_temp

        self.set(kwargs)

    def to_yaml(self) -> dict:
        """Convert object to YAML dict"""
        output = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }
        output["mash_steps"] = {}
        for step in getattr(self, "mash_steps", []):
            output["mash_steps"].update(step.to_yaml())

        return output


class MashStep(BeerComponent):

    def __init__(self, name, type, step_time, step_temp, **kwargs):
        super().__init__("mash_step")

        self.name = name
        self.type = type
        self.step_time = step_time
        self.step_temp = step_temp

        self.set(kwargs)
