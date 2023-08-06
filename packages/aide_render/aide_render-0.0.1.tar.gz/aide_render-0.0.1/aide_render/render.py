from aide_render import yaml
import jinja2
from aide_design.units import unit_registry as u
import aide_design
import numpy as np
import os
import sys
import re
from aide_design.play import *


from jinja2 import contextfunction, environmentfunction, evalcontextfunction


@contextfunction
def show_context(context):
    """Shows what you can do with the context

    Parameters
    ----------
    context

    Returns
    -------

    Examples
    --------

    >>> import jinja2
    >>> env = jinja2.Environment()
    >>> env.globals.update({"yo": "yodles"})
    >>> t = env.from_string("{{show_context()}}")
    >>> t.render({"local_variable":"hello", "show_context": show_context})
    a variable: hello
    the parent: <class 'dict'>
    the environment: <class 'jinja2.environment.Environment'>
    the variables: {}
    the exported_vars: set()
    the names: None
    the blocks: {}
    the eval_ctx: <class 'jinja2.nodes.EvalContext'>
    'None'


    """
    print("a variable:", context["local_variable"])
    print("the parent:", type(context.parent))
    print("the environment:", type(context.environment))
    print("the variables:", context.vars)
    print("the exported_vars:", context.exported_vars)
    print("the names:", context.name)
    print("the blocks:", context.blocks)
    print("the eval_ctx:", type(context.eval_ctx))


def strip_jinja(string: str):
    """
    Strip all Jinja tags from the string.
    >>> strip_jinja("hi there, a {{ jinja.statement }} and a {% jinja.expr %}")
    'hi there, a  and a '
    """
    # Match Jinja statements
    regex = re.compile("({{.*?}})")
    string = re.sub(regex, '', string)
    # Match Jinja expression
    regex = re.compile("({%.*?%})")
    string = re.sub(regex, '', string)
    # Match Jinja expression
    regex = re.compile("({#.*?#})")
    string = re.sub(regex, '', string)
    return re.sub(regex, '', string)

@environmentfunction
def render_constants(environment, template_string):
    """
    Strip all Jinja tags from a template and render the remaining constants as
    a dict.


    Parameters
    ----------
    environment: jinja2.Environment
        If this is called within a template, then the environment is automatically passed in and the template_string
        is assumed to be the source string of the template. If no environment is passed in (as in testing), the
        template_string is assumed to be the name of the template available to the environment's loader.

    template: string
        Either the template name if a context is passed in or the function is called within a template, or the source
        string if the context is passed as None (mainly for testing purposes.)

    Examples
    --------
    Jinja tags are returned as None:

    >>> render_constants(None, "{'a jinja statement':{{5*u.m}}, 'jinja expr':{%yo%}, 'cp': {'string expr': 'this works'}}")
    {'string expr': 'this works'}

    The aide_render YAML implementation parses the units tag explicitly (!u) and implicitly ( 5 meter)
    >>> render_constants(None, "{'cp': {'explicit unit':!q 20 meter, 'implicit unit': 36 meter**3, 'complex implicit unit': 0.25 meter**3/liter}}")
    {'explicit unit': <Quantity(20.0, 'meter')>, 'implicit unit': <Quantity(36.0, 'meter ** 3')>, 'complex implicit unit': <Quantity(0.25, 'meter ** 3 / liter')>}

    """

    if environment:
        template_string, filename, uptodate = environment.loader.get_source(environment, template_string)

    stripped_template = strip_jinja(template_string)
    try:
        doc = yaml.load(stripped_template)
    except yaml.composer.ComposerError:
        raise yaml.composer.ComposerError("The template has to have only one yaml doc defined.")

    t = type(doc)
    if not t == dict:
        raise ValueError("Template must parse into a dict. Template was parsed as a {}".format(str(t)))

    # Get just the cp variables:
    try:
        doc = doc["cp"]
    except KeyError:
        raise KeyError("Render constants only renders templates with a constants 'cp' tag")

    return doc


def source_from_path(file_path: str) -> str:
    """

    Parameters
    ----------
    file_path: Absolute path to the file to read.

    Returns
    -------
    str
        The contents of the file.

    """
    with open(file_path) as f:
        return f.read()


def assert_inputs(variables: dict, types_dict: dict, strict=True, silent=False, variables_explicit=None):
    """Check variables against their expected type. Also can check more complex types, such as whether the expected
    and actual dimensionality of pint units are equivalent. This can be used within a Jinja template, but when doing
    so, the "variables" argument is automatically filled with the context of the template.

    Parameters
    ----------
    variables : dict
        Contain variable_name : variable_object key-value pairs.
    types_dict : dict
        A dictionary containing variable:type key value pairs.
    strict :obj: bool, optional
        If true, the function ensures all the variables in types_dict are present in variables.
    silent :obj: bool, optional
        If true, the function only returns a boolean rather than throwing an error.

    Returns
    -------
    bool
        True if the variables dict passes the assert_inputs check as described.

    Raises
    ------
    ValueError
        If silent is turned to false and the inputs do not pass the assert_inputs test

    Examples
    --------

    Standard usage showing a passing collection of parameters. This passes both the non-strict and strict options.

    >>> variables = {"a" : 1, "b" : 1.0, "c" : "string"}
    >>> types_dict = {"a" : int, "b" : float, "c" : str}
    >>> assert_inputs(variables,types_dict)
    True

    Wrong types error thrown:

    >>> types_dict = {"a" : str, "b" : str, "c" : str}
    >>> assert_inputs(variables,types_dict)
    Traceback (most recent call last):
    TypeError: Can't convert the following implicitly: {'a': "Actual type: <class 'int'> Intended type: <class 'str'>", 'b': "Actual type: <class 'float'> Intended type: <class 'str'>"}.

    Not enough variables are present:
    >>> assert_inputs({"a":1}, {"a":int, "b": int})
    Traceback (most recent call last):
    NameError: names 'b' are not defined

    >>> from aide_design.play import *
    >>> assert_inputs({"length" : 1*u.meter},{"length" : u.mile})
    True
    >>> assert_inputs({"length" : 1*u.meter**2},{"length" : u.mile})
    Traceback (most recent call last):
    TypeError: Can't convert the following implicitly: {'length': 'Actual dimensionality: [length] ** 2 Intended dimensionality: [length]'}.

    """
    # Store the intended types
    type_error_dicionary = {}
    # Store the missing variables
    missing = []

    if variables_explicit:
        variables = variables_explicit

    for name, t in types_dict.items():
        try:
            var = variables[name]

            #check for recursive dicts. If there are, then recurse.
            if isinstance(t, dict):
                assert_inputs(var, t)

            # check if this is a pint variable and has compatible dimensionality.
            if isinstance(var, u.Quantity):
                if not var.dimensionality == t.dimensionality:
                    type_error_dicionary[name] = "Actual dimensionality: {} Intended dimensionality: {}".format(
                        var.dimensionality, t.dimensionality)

            # check if types are compatible
            elif not isinstance(var, t):
                type_error_dicionary[name] = "Actual type: {} Intended type: {}".format(type(var), t)

        # If the variable is missing
        except KeyError:
            missing.append(name)

    check = not type_error_dicionary
    if strict and check:
        check = not missing

    if not silent and not check:
        if missing:
            raise NameError("names {} are not defined".format("'" + "', '".join(missing) + "'"))
        if type_error_dicionary:
            raise TypeError("Can't convert the following implicitly: {}.".format(type_error_dicionary))
    return check


def start_aide_render(template_folder_path, template_to_render, user_params):
    from aide_render.import_dicts import aide_render_dict
    env = jinja2.Environment(
                             loader=jinja2.loaders.FileSystemLoader(template_folder_path),
                             trim_blocks=True,
                             lstrip_blocks=True,
                             )
    env.globals.update(aide_render_dict)
    return env.get_template(template_to_render).render(user_params)

@contextfunction
def get_context(context):
    return context