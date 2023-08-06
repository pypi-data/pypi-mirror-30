"""aide_render's YAML decomposition logic. aide_render uses standard pyYaml with
additional tags supported. Here's a list of the currently supported tags and
their use case:
  * !u: used with a unit string (ie: 5 meter) to represent a pint quantity.
  * !quantity: used to represent a pint quantity: <Quantity(1.25, 'liter / second')>
"""

from yaml import *
from aide_design.units import unit_registry as u
import re


############################### Representers and Constructors ###########################


def units_representer(dumper, data):
    return dumper.represent_scalar(u'!q', str(data))


def units_constructor(loader, node):
    value = loader.construct_scalar(node)
    pattern = re.compile(r'([ ]?[+-]?[0-9]*[.]?[0-9]+)')
    split_list = re.split(pattern, value)
    mag, units = split_list[1], ''.join(split_list[2:])
    return u.Quantity(float(mag), units)


############################### Turning on and off the tags ############################
# Use this section to comment out tags as necessary.


# !q tag and constructor
add_representer(u.Quantity, units_representer)
add_constructor(u'!q', units_constructor)
pattern = re.compile(r'[+-]?([0-9]*[.])?[0-9]+[ ]([A-z]+[/*]*[0-9]*)')
add_implicit_resolver(u'!q', pattern)
