from typing import (Any,
                    Tuple,
                    Type)
from liable.functions.detectors import (is_literal,
                                        supports_to_string)


def test_supports_to_string(object_: Any) -> None:
    result = supports_to_string(object_)

    assert isinstance(result, bool)


def test_is_literal(object_: Any,
                    basic_types: Tuple[Type]) -> None:
    result = is_literal(object_=object_,
                        basic_types=basic_types)

    assert isinstance(result, bool)
from liable.functions.detectors import (is_literal,
                                        supports_to_string)
from typing import (Any,
                    Tuple,
                    Type)


def test_supports_to_string(object_: Any) -> None:
    result = supports_to_string(object_)

    assert isinstance(result, bool)


def test_is_literal(object_: Any,
                    basic_types: Tuple[Type]) -> None:
    result = is_literal(object_=object_,
                        basic_types=basic_types)

    assert isinstance(result, bool)
