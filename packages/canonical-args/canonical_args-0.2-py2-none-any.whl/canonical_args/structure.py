"""
Provides utilities for checking the structure of a list
or dict against provided structure mandates and details.
"""
from __future__ import absolute_import

import json

from . import check



def check_list(names, types, values, arg):
    """
    recursively check a list of argument values (``arg``).
    usually used to check positional arguments passed to a
    function call.
    """
    # length
    try:
        assert len(types) == len(arg)
    except AssertionError as e:
        raise AssertionError("expected {} positional arguments, only"\
                             " got {}".format(len(types), len(arg)))

    for subname, subtype, subvalues, subarg in zip(names, types, values, arg):

        subtype = check.eval_subtype(subtype)
        
        # recurse if list or tuple
        if (isinstance(subtype, list) or
            isinstance(subtype, tuple)):
            subname = ["{}#{}".format(subname, i) \
                       for i in range(0, len(subtype))]
            check_list(subname, subtype, subvalues, subarg)
            continue

        elif isinstance(subtype, dict):
            check_dict(subtype, subarg)
            continue

        subarg = check.check_subtype(subname, subtype, subarg)
        check.check_value(subname, subvalues, subarg)


def check_dict(structure_dict, kwargs):
    """
    usually used for checking kwargs
    """
    required = [key for key, spec in structure_dict.items()\
                    if "required" not in spec or spec["required"]]

    # keys may not be missing
    missing = set(required) - set(kwargs.keys())
    assert len(missing) == 0

    for subname, subarg in kwargs.items():
        # make sure the keyword argument is registered
        assert subname in structure_dict
        struct = structure_dict[subname]

        subtype = check.eval_subtype(struct["type"])

        if isinstance(subtype, list) or isinstance(subtype, tuple):
            subname = ["{}#{}".format(subname, i) for i in range(0, len(subtype))]
            check_list(subname, subtype, struct["values"], subarg)
            continue

        elif isinstance(subtype, dict):
            check_dict(subtype, subarg)
            continue

        subarg = check.check_subtype(subname, subtype, subarg)
        check.check_value(subname, struct["values"], subarg)


def check_args(struct, args, kwargs):
    """
    check the arguments provided against the structure.

    :param dict struct: the dict detailing the argument structure
    :param list args: the args to check against struct
    :param dict kwargs: the kwargs to check against the struct
    :raises AssertionError: when args or kwargs do not match struct
    """
    names = [sub["name"] for sub in struct["args"]]
    types = [sub["type"] for sub in struct["args"]]
    values = [sub["values"] for sub in struct["args"]]
    # args = args

    check_list(names, types, values, args)
    if kwargs:  # kwargs are optional!
        check_dict(struct["kwargs"], kwargs)

