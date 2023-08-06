from types import FunctionType
from hypothesis import strategies
import inspect
from liable.catalog import (ContentPath,
                            ModulePath)
objects_paths_iterable = strategies.iterables(strategies.one_of(strategies.builds(ModulePath),
                                                                strategies.builds(ContentPath)))
modules_parameters_iterable = strategies.iterables(strategies.builds(inspect.Parameter,
                                                                     name=strategies.none(),
                                                                     kind=strategies.none(),
                                                                     default=strategies.none(),
                                                                     annotation=strategies.none()))
paths_iterable = strategies.iterables(strategies.text())
parameters_iterable = strategies.iterables(strategies.builds(inspect.Parameter,
                                                             name=strategies.none(),
                                                             kind=strategies.none(),
                                                             default=strategies.none(),
                                                             annotation=strategies.none()))
modules_functions_iterable = strategies.iterables(
    strategies.builds(FunctionType))
types_iterable = strategies.iterables(strategies.builds(type,
                                                        strategies.from_regex(
                                                            '\A[_a-zA-Z]+\Z'),
                                                        strategies.tuples(),
                                                        strategies.builds(dict)))
other_types_iterable = strategies.iterables(strategies.builds(type,
                                                              strategies.from_regex(
                                                                  '\A[_a-zA-Z]+\Z'),
                                                              strategies.tuples(),
                                                              strategies.builds(dict)))
systems_paths_iterable = strategies.iterables(strategies.text())
words_iterable = strategies.iterables(strategies.text())
functions_iterable = strategies.iterables(strategies.builds(FunctionType))
from types import FunctionType
from hypothesis import strategies
from liable.catalog import (ContentPath,
                            ModulePath)
import inspect
objects_paths_iterable = strategies.iterables(strategies.one_of(strategies.builds(ModulePath),
                                                                strategies.builds(ContentPath)))
systems_paths_iterable = strategies.iterables(strategies.text())
parameters_iterable = strategies.iterables(strategies.builds(inspect.Parameter,
                                                             name=strategies.none(),
                                                             kind=strategies.none(),
                                                             default=strategies.none(),
                                                             annotation=strategies.none()))
modules_paths_iterable = strategies.iterables(strategies.text())
modules_functions_iterable = strategies.iterables(
    strategies.builds(FunctionType))
types_iterable = strategies.iterables(strategies.builds(type,
                                                        strategies.from_regex(
                                                            '\A[_a-zA-Z]+\Z'),
                                                        strategies.tuples(),
                                                        strategies.builds(dict)))
other_types_iterable = strategies.iterables(strategies.builds(type,
                                                              strategies.from_regex(
                                                                  '\A[_a-zA-Z]+\Z'),
                                                              strategies.tuples(),
                                                              strategies.builds(dict)))
modules_parameters_iterable = strategies.iterables(strategies.builds(inspect.Parameter,
                                                                     name=strategies.none(),
                                                                     kind=strategies.none(),
                                                                     default=strategies.none(),
                                                                     annotation=strategies.none()))
words_iterable = strategies.iterables(strategies.text())
paths_iterable = strategies.iterables(strategies.text())
functions_iterable = strategies.iterables(strategies.builds(FunctionType))
