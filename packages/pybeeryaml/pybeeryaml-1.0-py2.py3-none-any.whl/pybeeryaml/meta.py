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


import keyword
import xml.etree.ElementTree as ET


class BeerComponent:
    """Base class for beer component"""

    def __init__(self, objname=None, **kwargs):
        self.version = 1
        self._objname = objname or self.__class__.__name__

    def set(self, data: dict):
        """Set optional data"""
        for key, value in data.items():
            if isinstance(value, list):
                continue

            if keyword.iskeyword(key):
                key = f"beeryaml_{key}"

            setattr(self, key, value)

    def to_yaml(self) -> dict:
        """Convert object to YAML dict"""
        output = {}
        output[self.name] = {}

        for key, value in self.__dict__.items():
            if key.startswith("_") or key == "name":
                continue
            elif key.startswith("beeryaml_"):
                key = key[9:]

            if isinstance(value, BeerComponent):
                data = value.to_yaml()
                output[self.name].update(data)
            elif isinstance(value, list):
                output[self.name][key] = {}
                for elt in value:
                    output[self.name][key].update(elt.to_yaml())
            else:
                output[self.name][key] = value

        return output

    def to_xml(self) -> str:
        """Convert to beerxml format"""
        root = ET.Element(self._objname.upper())
        for key, value in self.__dict__.items():

            if key.startswith("_"):
                continue
            elif key.startswith("beeryaml_"):
                key = key[9:]

            if isinstance(value, BeerComponent):
                root.append(ET.fromstring(value.to_xml()))
            else:
                subelt = ET.SubElement(root, key.upper())

                if isinstance(value, list):
                    for elt in value:
                        subelt.append(ET.fromstring(elt.to_xml()))
                else:
                    subelt.text = str(value)

        return ET.tostring(root)
