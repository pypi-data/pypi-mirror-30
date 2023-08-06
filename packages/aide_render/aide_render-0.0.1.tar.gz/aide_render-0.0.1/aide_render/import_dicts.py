"""These are dicts of python objects that can be passed along to the rendering engine for use within a jinja
environment. To use, simply import the dict from your file, ie: from aide_render.import_dicts import aide_render_dict"""

from aide_render.render import *

aide_render_dict = {"u": u, "os": os, "render_constants": render_constants, "assert_inputs":
    assert_inputs, "dict": dict, "show_context": show_context, "str": str, "float": float, "np": np, "dump": yaml.dump,
                    "get_context": get_context}