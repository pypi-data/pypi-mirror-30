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


from yaml import safe_load
from keyword import iskeyword
from pybeeryaml.hop import Hop
from pybeeryaml.yeast import Yeast
from pybeeryaml.meta import BeerComponent
from pybeeryaml.misc import Misc
from pybeeryaml.water import Water
from pybeeryaml.style import Style
from pybeeryaml.fermentable import Fermentable
from pybeeryaml.mash import MashProfile, MashStep


class Recipe(BeerComponent):
    """Recipe model

    :param data: dict recipe data
    """

    def __init__(self, data: dict):
        super().__init__()
        self.set(data)

        if hasattr(self, "style") and isinstance(self.style, dict):
            self.style = Style(**data["style"])

        hops = self.flatten(data.get("hops", {}))
        self.hops = [Hop(**hdata) for hdata in hops]

        yeasts = self.flatten(data.get("yeasts", {}))
        self.yeasts = [Yeast(**ydata) for ydata in yeasts]

        ferments = self.flatten(data.get("fermentables", {}))
        self.fermentables = [Fermentable(**fdata) for fdata in ferments]

        miscs = self.flatten(data.get("miscs", {}))
        self.miscs = [Misc(**mdata) for mdata in miscs]

        profile = data.get("mash", {"name": "mash", "grain_temp": 25})
        self.mash = MashProfile(**profile)

        steps = []
        if hasattr(self.mash, "mash_steps"):
            msdata = self.flatten(self.mash.mash_steps)
            for mash_step in msdata:
                steps.append(MashStep(**mash_step))

        self.mash.mash_steps = steps

        waters = self.flatten(data.get("waters", {}))
        self.waters = [Water(wdata) for wdata in waters]

    def flatten(self, data: dict) -> list:
        """Flatten yaml dict

        :param data: YAML dict
        """
        output = []
        for key, value in data.items():
            if isinstance(value, dict):
                value["name"] = key

                for vkey, vvalue in value.items():
                    if iskeyword(vkey):
                        value[f"beeryaml_{vkey}"] = vvalue
                        del value[vkey]

            output.append(value)
        return output

    def to_yaml(self) -> dict:
        """Convert object to YAML dict"""
        output = {}

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            elif key.startswith("beeryaml_"):
                key = key[9:]

            if value:
                if isinstance(value, BeerComponent) and key != "mash":
                    data = value.to_yaml()
                    output.update(data)
                elif isinstance(value, list):
                    output[key] = {}
                    for elt in value:
                        output[key].update(elt.to_yaml())
                else:
                    output[key] = value

        # mash
        output["mash"] = self.mash.to_yaml()

        return output

    @classmethod
    def from_file(cls, filepath: str):
        """Create recipe from YAML file

        :param filepath: YAML file containing recipe data
        """
        with open(filepath, "r") as fi:
            data = safe_load(fi.read())
        return cls(data)

    @classmethod
    def from_yaml(cls, data: str):
        """Create recipe from YAML data

        :param data: YAML recipe data
        """
        return cls(safe_load(data))
