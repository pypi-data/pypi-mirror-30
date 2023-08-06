from typing import (Any,
                    Type)
from liable.annotator.utils import (none_type_to_none,
                                    normalize,
                                    to_annotation,
                                    walk)
import collections
from liable.annotator.base import Annotation
from liable.types import NamespaceType


def test_normalize(type_: Type) -> None:
    result = normalize(type_)

    assert isinstance(result, Annotation)


def test_to_annotation(object_: Any) -> None:
    result = to_annotation(object_)

    assert isinstance(result, Annotation)


def test_walk(annotation: Annotation,
              namespace: NamespaceType) -> None:
    result = walk(annotation=annotation,
                  namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_none_type_to_none(object_: Any) -> None:
    result = none_type_to_none(object_)

    assert isinstance(result, object)
from liable.annotator.base import Annotation
from liable.annotator.utils import (none_type_to_none,
                                    normalize,
                                    to_annotation,
                                    walk)
import collections
from typing import (Any,
                    Type)
from liable.types import NamespaceType


def test_normalize(type_: Type) -> None:
    result = normalize(type_)

    assert isinstance(result, Annotation)


def test_to_annotation(object_: Any) -> None:
    result = to_annotation(object_)

    assert isinstance(result, Annotation)


def test_walk(annotation: Annotation,
              namespace: NamespaceType) -> None:
    result = walk(annotation=annotation,
                  namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_none_type_to_none(object_: Any) -> None:
    result = none_type_to_none(object_)

    assert isinstance(result, object)
