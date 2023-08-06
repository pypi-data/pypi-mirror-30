# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .utils import get_maximum_value, get_function_name
from bw2data import DataStore, Method, methods
from bw2data.serialization import SerializedDict
from bw2data.utils import random_string
import warnings


class FunctionWrapper(object):
    def __init__(self, func_string):
        self.func_name = get_function_name(func_string)
        if not self.func_name:
            raise ValueError
        exec(func_string)
        self.function = locals()[self.func_name]

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


class DynamicMethods(SerializedDict):
    """A dictionary for dynamic impact assessment method metadata. File data is saved in ``dynamic-methods.json``."""
    filename = "dynamic-methods.json"


dynamic_methods = DynamicMethods()


class DynamicIAMethod(DataStore):
    """A dynamic impact assessment method. Not translated into matrices, so no ``process`` method."""
    _metadata = dynamic_methods

    def to_worst_case_method(self, name, lower=None, upper=None, dynamic=True,register=True):
        """Create a static LCA method using the worst case for each dynamic CF function.
        Default time interval over which to test for maximum CF is `datetime.now()` to `datetime.now()+relativedelta(years=100)`.
        
Args:
    * *name* (string): method name.
    * *lower* (datetime, default=datetime(2010, 1, 1): lower bound of the interval to consider.
    * *upper* (datetime, default=lower + relativedelta(years=100): upper bound of the interval to consider.
    * *dynamic* (bool, default=True): If total CF function of time of emission 
    * *register* (bool, default=True): If to register the method   

        """
        kwargs = {'dynamic': dynamic}
        if lower is not None:
            kwargs['lower'] = lower
        if upper is not None:
            kwargs['upper'] = upper
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            worst_case_method = Method(tuple(name))
            if worst_case_method.name not in methods:
                worst_case_method.register(dynamic_method = self.name)
        data = self.load()
        data.update(self.create_functions())
        # for now just characterize all the 'Carbon dioxide, in air' to be sure they are not skipped
        # should think better on how to deal with this
        method=[
        [('biosphere3', 'cc6a1abb-b123-4ca6-8f16-38209df609be'),abs(get_maximum_value(value, **kwargs))] if key == ('static_forest',"C_biogenic") else 
        [key, abs(get_maximum_value(value, **kwargs))] for key, value in data.items()
        ]
        #needed for GWP function to avoid registration every time
        if not register:
            return method
        worst_case_method.write(method)
        worst_case_method.process() #GIU: guess not needed anymore right?
        return worst_case_method

    def from_static_method(self, name):
        """Turn a static LCIA method into a dynamic one.

        The dynamic method should not be registered yet.

        `name` is the name (tuple) of an existing static method."""
        assert name in methods, "Method {} not found".format(name)
        cfs = {obj[0]: obj[1]
               for obj in Method(name).load()
               if (len(obj) == 2 or obj[2] == 'GLO')}
        metadata = copy.deepcopy(methods[name])
        metadata['from_static_method'] = name
        self.register(**metadata)
        self.write(cfs)

    def create_functions(self, data=None):
        """Take method data that defines functions in strings, and turn them into actual Python code. Returns a dictionary with flows as keys and functions as values."""
        if data is None:
            data = self.load()
        prefix = "created_function_{}_".format(random_string())
        functions = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Backwards compatibility
                if '%s' in value:
                    warnings.simplefilter('always', DeprecationWarning) #otherwise not warning and fail to pass test
                    warnings.warn(
                        "Functions can now be normal Python code; please change def %s() to def some_name().",
                        DeprecationWarning
                    )
                    value = value % "created_function"
                functions[key] = FunctionWrapper(value)
        return functions
