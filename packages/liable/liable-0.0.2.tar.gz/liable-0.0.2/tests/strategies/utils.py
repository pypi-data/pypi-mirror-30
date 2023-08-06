import ast
from hypothesis import strategies
from liable.catalog import (ContentPath,
                            ModulePath)
import inspect
from types import ModuleType
objects_paths = strategies.one_of(strategies.builds(ModulePath),
                                  strategies.builds(ContentPath))
paths = strategies.text()
fulls_names = strategies.text()
files_names = strategies.text()
modules_objects_paths_tuple = strategies.tuples(strategies.one_of(strategies.builds(ModulePath),
                                                                  strategies.builds(ContentPath)))
objects = strategies.none()
modules_parameters_dict = strategies.dictionaries(strategies.builds(ModulePath),
                                                  strategies.lists(strategies.builds(inspect.Parameter,
                                                                                     name=strategies.none(),
                                                                                     kind=strategies.none(),
                                                                                     default=strategies.none(),
                                                                                     annotation=strategies.none())))
namespace_dict = strategies.dictionaries(strategies.one_of(strategies.builds(ModulePath),
                                                           strategies.builds(ContentPath)),
                                         strategies.none())
objects_tuple = strategies.tuples(strategies.none())
mappings_tuple = strategies.tuples(strategies.dictionaries(strategies.integers(),
                                                           strategies.none()))
commons_modules_paths = strategies.text()
types_types = strategies.builds(type,
                                strategies.from_regex('\A[_a-zA-Z]+\Z'),
                                strategies.tuples(),
                                strategies.builds(dict))
other_types_types = strategies.builds(type,
                                      strategies.from_regex('\A[_a-zA-Z]+\Z'),
                                      strategies.tuples(),
                                      strategies.builds(dict))
modules_dict = strategies.dictionaries(strategies.builds(ModulePath),
                                       strategies.builds(ModuleType))
sources = strategies.text()
modes = strategies.text()
permissible_extensions_tuple = strategies.tuples(strategies.text())
statements = strategies.one_of(strategies.builds(ast.Import),
                               strategies.builds(ast.ImportFrom))
all_objects_wildcard = strategies.text()
recursive = strategies.booleans()
directories = strategies.text()
subs_directories_tuple = strategies.tuples(strategies.text())
spaces_counts = strategies.integers()
sources_extensions = strategies.text()
strings_tuple = strategies.tuples(strategies.text())
seps = strategies.text()
strings = strategies.text()
words = strategies.text()
tests_modules_names = strategies.text()
strategies_modules_names = strategies.text()
basics_types_tuple = strategies.tuples(strategies.builds(type,
                                                         strategies.from_regex(
                                                             '\A[_a-zA-Z]+\Z'),
                                                         strategies.tuples(),
                                                         strategies.builds(dict)))
from hypothesis import strategies
import ast
from liable.catalog import (ContentPath,
                            ModulePath)
import inspect
from types import ModuleType
sources = strategies.text()
files_names = strategies.text()
modes = strategies.text()
permissible_extensions_tuple = strategies.tuples(strategies.text())
statements = strategies.one_of(strategies.builds(ast.Import),
                               strategies.builds(ast.ImportFrom))
all_objects_wildcard = strategies.text()
paths = strategies.text()
objects_paths = strategies.one_of(strategies.builds(ModulePath),
                                  strategies.builds(ContentPath))
fulls_names = strategies.text()
modules_objects_paths_tuple = strategies.tuples(strategies.one_of(strategies.builds(ModulePath),
                                                                  strategies.builds(ContentPath)))
objects = strategies.none()
recursive = strategies.booleans()
directories = strategies.text()
subs_directories_tuple = strategies.tuples(strategies.text())
namespace_dict = strategies.dictionaries(strategies.one_of(strategies.builds(ModulePath),
                                                           strategies.builds(ContentPath)),
                                         strategies.none())
spaces_counts = strategies.integers()
tests_modules_names = strategies.text()
strategies_modules_names = strategies.text()
tops_directories = strategies.text()
modules_fulls_names = strategies.text()
sources_extensions = strategies.text()
overwrite = strategies.booleans()
modules_dict = strategies.dictionaries(strategies.builds(ModulePath),
                                       strategies.builds(ModuleType))
commons_modules_paths = strategies.text()
types_types = strategies.builds(type,
                                strategies.from_regex('\A[_a-zA-Z]+\Z'),
                                strategies.tuples(),
                                strategies.builds(dict))
other_types_types = strategies.builds(type,
                                      strategies.from_regex('\A[_a-zA-Z]+\Z'),
                                      strategies.tuples(),
                                      strategies.builds(dict))
modules_parameters_dict = strategies.dictionaries(strategies.builds(ModulePath),
                                                  strategies.lists(strategies.builds(inspect.Parameter,
                                                                                     name=strategies.none(),
                                                                                     kind=strategies.none(),
                                                                                     default=strategies.none(),
                                                                                     annotation=strategies.none())))
objects_tuple = strategies.tuples(strategies.none())
strings_tuple = strategies.tuples(strategies.text())
seps = strategies.text()
strings = strategies.text()
words = strategies.text()
mappings_tuple = strategies.tuples(strategies.dictionaries(strategies.integers(),
                                                           strategies.none()))
basics_types_tuple = strategies.tuples(strategies.builds(type,
                                                         strategies.from_regex(
                                                             '\A[_a-zA-Z]+\Z'),
                                                         strategies.tuples(),
                                                         strategies.builds(dict)))
