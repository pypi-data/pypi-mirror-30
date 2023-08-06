from liable.catalog import (ModulePath,
                            PathType)
from hypothesis import strategies
from liable.strings import Case
from liable.annotator.base import Annotation
annotations = strategies.builds(Annotation,
                                origin=strategies.builds(type,
                                                         strategies.from_regex(
                                                             '\A[_a-zA-Z]+\Z'),
                                                         strategies.tuples(),
                                                         strategies.builds(dict)))
modules_paths = strategies.builds(ModulePath)
other_annotations = strategies.builds(Annotation,
                                      origin=strategies.builds(type,
                                                               strategies.from_regex(
                                                                   '\A[_a-zA-Z]+\Z'),
                                                               strategies.tuples(),
                                                               strategies.builds(dict)))
previous_annotations = strategies.builds(Annotation,
                                         origin=strategies.builds(type,
                                                                  strategies.from_regex(
                                                                      '\A[_a-zA-Z]+\Z'),
                                                                  strategies.tuples(),
                                                                  strategies.builds(dict)))
targets_cases = strategies.builds(Case)
paths_types = strategies.builds(PathType)
from liable.strings import Case
from liable.catalog import (ModulePath,
                            PathType)
from liable.annotator.base import Annotation
from hypothesis import strategies
modules_paths = strategies.builds(ModulePath)
paths_types = strategies.builds(PathType)
annotations = strategies.builds(Annotation,
                                origin=strategies.builds(type,
                                                         strategies.from_regex(
                                                             '\A[_a-zA-Z]+\Z'),
                                                         strategies.tuples(),
                                                         strategies.builds(dict)))
other_annotations = strategies.builds(Annotation,
                                      origin=strategies.builds(type,
                                                               strategies.from_regex(
                                                                   '\A[_a-zA-Z]+\Z'),
                                                               strategies.tuples(),
                                                               strategies.builds(dict)))
previous_annotations = strategies.builds(Annotation,
                                         origin=strategies.builds(type,
                                                                  strategies.from_regex(
                                                                      '\A[_a-zA-Z]+\Z'),
                                                                  strategies.tuples(),
                                                                  strategies.builds(dict)))
targets_cases = strategies.builds(Case)
