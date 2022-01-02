# -*- coding: utf-8 -*-
"""Testing utility to play back usage scenarios for estimators.

Contains TestScenario class which applies method/args subsequently
"""

__author__ = ["fkiraly"]

__all__ = ["TestScenario"]


from copy import deepcopy
import numpy as np


class TestScenario:
    """Class to run pre-defined method execution scenarios for objects.

    Parameters
    ----------
    args : dict of dict, default = None
        dict of argument dicts to be used in methods
        names for keys need not equal names of methods these are used in
            but scripted method will look at key with same name as default
        must be passed to construtor, or set in a child class
    default_method_sequence : list of str, default = None
        optional, if given, default method sequence to use in "run"
        if not provided, "run" must alwayss be passed a method_sequence

    Methods
    -------
    run(obj, args=None, default_method_sequence=None)
        Run a call(args) scenario on obj, and retrieve method outputs.
    """

    def __init__(self, args=None, default_method_sequence=None):

        if default_method_sequence is not None:
            self.default_method_sequence = _check_list_of_str(default_method_sequence)
        if args is not None:
            self.args = _check_dict_of_dict(args)
        else:
            if not hasattr(self, args):
                raise RuntimeError(
                    "args must either be given to __init__ or set in a child class"
                )
            _check_dict_of_dict(self.args)

    def run(self, obj, arg_sequence=None, method_sequence=None, return_all=False):
        """Run a call(args) scenario on obj, and retrieve method outputs.

        Runs a sequence of commands
            res_1 = obj.method_1(**args_1)
            res_2 = obj.method_2(**args_2)
            etc, where method_i is method_sequence[i],
                and args_i is arg_sequence[i]
        and returns results.

        if method_i is __init__ (a constructor),
        obj is changed to obj.__init__(**args_i) from the next line on

        Parameters
        ----------
        obj : class or object with methods in method_sequence
        method_sequence : list of str, default = method_sequence
            sequence of method names to be run
        arg_sequence : list of str, default = self.default_method_sequence
            sequence of keys for keyword argument dicts to be used
            names for keys need not equal names of methods
        return_all : bool, default = False
            whether all or only the last result should be returned
            if False, only the last result is returned
            if True, deepcopy of all intermediate results is returned

        Returns
        -------
        output of the last method call, if return_all = False
        list of deepcopies of all outputs, if return_all = True
        """
        if method_sequence is None:
            method_sequence = self.default_method_sequence
        else:
            method_sequence = _check_list_of_str(method_sequence)
        if arg_sequence is None:
            arg_sequence = method_sequence
        else:
            arg_sequence = _check_list_of_str(arg_sequence)

        num_calls = len(arg_sequence)
        if not num_calls == len(method_sequence):
            raise ValueError("arg_sequence and method_sequence must have same length")

        results = []
        for i in range(num_calls):
            methodname = method_sequence[i]
            args = self.args[arg_sequence[i]]
            res = getattr(obj, methodname)(**args)
            if methodname == "__init__":
                obj = res
            if return_all:
                results += [deepcopy(res)]
            else:
                results = res

        return results


def _check_list_of_str(obj, name="obj"):
    """Check whether obj is a list of str.

    Parameters
    ----------
    obj : any object, check whether is list of str
    name : str, default="obj", name of obj to display in error message

    Returns
    -------
    obj, unaltered

    Raises
    ------
    TypeError if obj is not list of str
    """
    if not isinstance(obj, list) or not np.all(isinstance(x, str) for x in obj):
        raise TypeError(f"{obj} must be a list of str")
    return obj


def _check_dict_of_dict(obj, name="obj"):
    """Check whether obj is a dict of dict, with str keys.

    Parameters
    ----------
    obj : any object, check whether is dict of dict, with str keys
    name : str, default="obj", name of obj to display in error message

    Returns
    -------
    obj, unaltered

    Raises
    ------
    TypeError if obj is not dict of dict, with str keys
    """
    msg = f"{obj} must be a dict of dict, with str keys"
    if not isinstance(obj, dict):
        raise TypeError(msg)
    if not np.all(isinstance(x, dict) for x in obj.values()):
        raise TypeError(msg)
    if not np.all(isinstance(x, str) for x in obj.keys()):
        raise TypeError(msg)
    return obj
