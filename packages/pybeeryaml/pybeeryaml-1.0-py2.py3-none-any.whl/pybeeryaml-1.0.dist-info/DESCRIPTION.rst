pybeeryaml
==========

A YAML format parser for beer storage

Parse a recipe from a YAML file and returns an object containing ingredients and
metadata. Supports export to `beerxml <http://beerxml.com/>`_ format.

Installation
------------

.. code:: sh

    pip install pybeeryaml

Usage
-----

.. code:: python

    from pybeeryaml import Recipe

    path_to_beeryaml_file = "/tmp/my_recipe.yml"

    # create recipe from file
    recipe = Recipe.from_file(path_to_beeryaml_file)

    # or from string
    with open(path_to_beeryaml_file, "r") as mybeer:
        recipe2 = Recipe.from_yaml(mybeer.read())

    assert recipe == recipe2  # True

    # convert to beerxml format
    recipexml = recipe.to_xml()


Testing
-------

Unit tests can be run with `pytest <https://docs.pytest.org/en/latest/>`_.

.. code:: sh

    py.test tests


