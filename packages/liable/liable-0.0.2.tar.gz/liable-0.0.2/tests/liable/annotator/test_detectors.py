from liable.annotator.detectors import (is_callable,
                                        is_generic,
                                        is_none_annotation,
                                        is_typing)
from typing import (Any,
                    Type)
from liable.annotator.base import Annotation


def test_is_callable(type_: Type) -> None:
    result = is_callable(type_)

    assert isinstance(result, bool)


def test_is_none_annotation(annotation: Annotation) -> None:
    result = is_none_annotation(annotation)

    assert isinstance(result, bool)


def test_is_typing(object_: Any) -> None:
    result = is_typing(object_)

    assert isinstance(result, bool)


def test_is_generic(object_: Any) -> None:
    result = is_generic(object_)

    assert isinstance(result, bool)
from liable.annotator.detectors import (is_callable,
                                        is_generic,
                                        is_none_annotation,
                                        is_typing)
from liable.annotator.base import Annotation
from typing import (Any,
                    Type)


def test_is_callable(type_: Type) -> None:
    result = is_callable(type_)

    assert isinstance(result, bool)


def test_is_none_annotation(annotation: Annotation) -> None:
    result = is_none_annotation(annotation)

    assert isinstance(result, bool)


def test_is_typing(object_: Any) -> None:
    result = is_typing(object_)

    assert isinstance(result, bool)


def test_is_generic(object_: Any) -> None:
    result = is_generic(object_)

    assert isinstance(result, bool)
