"""

"""
from __future__ import absolute_import



def dynamic_import(class_string):
    """
    perform a dynamic import of a class or function (callable).
    """
    package_name = class_string.split(".")[0]

    mod = __import__(package_name)
    for comp in class_string.split(".")[1:]:
        mod = getattr(mod, comp)
    return mod

def eval_subtype(subtype):
    """

    """
    if isinstance(subtype, str) or isinstance(subtype, unicode):
        try:
            subtype = eval(subtype)
        except NameError:
            # THIS IS A CLASS, not a type!!!!!!
            subtype = dynamic_import(subtype)

    return subtype

def check_subtype(subname, subtype, subarg, should_cast=False):
    """

    """
    try:
        assert isinstance(subarg, subtype) or subarg is None
    except AssertionError as e:
        if should_cast:
            try:
                subarg = subtype(subarg)
            except ValueError as e:
                raise ValueError("unable to cast argument '{}' of"\
                                 "type {} to type {}".format(
                    subname, type(subarg), subtype))
        else:
            raise AssertionError("expected argument '{}' of type {}."\
                                 " got {}".format(
                subname, subtype, type(subarg)))
    return subarg

def check_value(subname, subvalues, subarg):
    """

    """
    # whitelisting
    check_value_whitelist(subname, subvalues, subarg)

    # number ranging (int and float)
    check_value_range(subname, subvalues, subarg)

    # number gt, lt, gte, lte
    check_value_comparison(subname, subvalues, subarg)

def check_value_whitelist(subname, subvalues, subarg):
    """

    """
    if isinstance(subvalues, list):
        try:
            assert subarg in subvalues
        except AssertionError as e:
            raise AssertionError("`{}` is not a permitted value for"\
                                 " arg '{}'. expected value from"\
                                 " {}".format(subarg, subname, subvalues))

def check_value_range(subname, subvalues, subarg):
    """

    """
    # number ranging (int and float)
    if ((isinstance(subvalues, str) or
         isinstance(subvalues, unicode)) and
        subvalues.startswith("range")):
        
        ran = eval(subvalues.replace("range", ""))
        try:
            assert ran[0] <= subarg and subarg <= ran[-1]
        except AssertionError as e:
            raise AssertionError("`{}` is not in range({}, {}) for"\
                                 " arg '{}'".format(subarg,
                                                    ran[0],
                                                    ran[-1],
                                                    subname))

def check_value_comparison(subname, subvalues, subarg):
    """

    """
    if ((isinstance(subvalues, str) or
         isinstance(subvalues, unicode)) and
        (subvalues.startswith(">") or subvalues.startswith("<"))):

        ts = "{}{}".format(subarg, subvalues)
        try:
            assert eval(ts)
        except AssertionError as e:
            raise AssertionError("`{}` is not {} for arg {}".format(
                subarg, subvalues, subname))

