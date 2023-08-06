import inflect
from liable.strings import (Case,
                            guess_case,
                            is_camel_case,
                            is_noun,
                            is_snake_case,
                            is_upper_case,
                            iterative_join,
                            join,
                            join_with_wrapping,
                            split_camel_case,
                            split_words,
                            to_camel,
                            to_plural,
                            to_plurals,
                            to_snake,
                            to_upper,
                            wrap_with_quotes)
from typing import (Iterable,
                    Sequence,
                    Tuple)
import collections


def test_join(strings: Iterable[str],
              sep: str) -> None:
    result = join(strings=strings,
                  sep=sep)

    assert isinstance(result, str)


def test_join_with_wrapping(strings: Sequence[str],
                            sep: str) -> None:
    result = join_with_wrapping(strings=strings,
                                sep=sep)

    assert isinstance(result, str)


def test_wrap_with_quotes(string: str) -> None:
    result = wrap_with_quotes(string)

    assert isinstance(result, object)


def test_to_plurals(string: str,
                    target_case: Case) -> None:
    result = to_plurals(string=string,
                        target_case=target_case)

    assert isinstance(result, str)


def test_guess_case(string: str) -> None:
    result = guess_case(string)

    assert isinstance(result, Case)


def test_split_words(string: str) -> None:
    result = split_words(string)

    assert isinstance(result, collections.Iterator)


def test_split_camel_case(string: str) -> None:
    result = split_camel_case(string)

    assert isinstance(result, collections.Iterator)


def test_is_camel_case(string: str) -> None:
    result = is_camel_case(string)

    assert isinstance(result, bool)


def test_is_snake_case(string: str) -> None:
    result = is_snake_case(string)

    assert isinstance(result, bool)


def test_is_upper_case(string: str) -> None:
    result = is_upper_case(string)

    assert isinstance(result, bool)


def test_to_plural(word: str,
                   engine: inflect.engine) -> None:
    result = to_plural(word=word,
                       engine=engine)

    assert isinstance(result, str)


def test_to_upper(words: Iterable[str]) -> None:
    result = to_upper(words)

    assert isinstance(result, str)


def test_to_camel(words: Iterable[str]) -> None:
    result = to_camel(words)

    assert isinstance(result, str)


def test_to_snake(words: Iterable[str]) -> None:
    result = to_snake(words)

    assert isinstance(result, str)


def test_is_noun(word: str) -> None:
    result = is_noun(word)

    assert isinstance(result, bool)


def test_iterative_join(strings: Tuple[str],
                        sep: str) -> None:
    result = iterative_join(*strings,
                            sep=sep)

    assert isinstance(result, collections.Iterator)
from typing import (Iterable,
                    Sequence,
                    Tuple)
from liable.strings import (Case,
                            guess_case,
                            is_camel_case,
                            is_noun,
                            is_snake_case,
                            is_upper_case,
                            iterative_join,
                            join,
                            join_with_wrapping,
                            split_camel_case,
                            split_words,
                            to_camel,
                            to_plural,
                            to_plurals,
                            to_snake,
                            to_upper,
                            wrap_with_quotes)
import collections
import inflect


def test_join(strings: Iterable[str],
              sep: str) -> None:
    result = join(strings=strings,
                  sep=sep)

    assert isinstance(result, str)


def test_join_with_wrapping(strings: Sequence[str],
                            sep: str) -> None:
    result = join_with_wrapping(strings=strings,
                                sep=sep)

    assert isinstance(result, str)


def test_wrap_with_quotes(string: str) -> None:
    result = wrap_with_quotes(string)

    assert isinstance(result, object)


def test_to_plurals(string: str,
                    target_case: Case) -> None:
    result = to_plurals(string=string,
                        target_case=target_case)

    assert isinstance(result, str)


def test_guess_case(string: str) -> None:
    result = guess_case(string)

    assert isinstance(result, Case)


def test_split_words(string: str) -> None:
    result = split_words(string)

    assert isinstance(result, collections.Iterator)


def test_split_camel_case(string: str) -> None:
    result = split_camel_case(string)

    assert isinstance(result, collections.Iterator)


def test_is_camel_case(string: str) -> None:
    result = is_camel_case(string)

    assert isinstance(result, bool)


def test_is_snake_case(string: str) -> None:
    result = is_snake_case(string)

    assert isinstance(result, bool)


def test_is_upper_case(string: str) -> None:
    result = is_upper_case(string)

    assert isinstance(result, bool)


def test_to_plural(word: str,
                   engine: inflect.engine) -> None:
    result = to_plural(word=word,
                       engine=engine)

    assert isinstance(result, str)


def test_to_upper(words: Iterable[str]) -> None:
    result = to_upper(words)

    assert isinstance(result, str)


def test_to_camel(words: Iterable[str]) -> None:
    result = to_camel(words)

    assert isinstance(result, str)


def test_to_snake(words: Iterable[str]) -> None:
    result = to_snake(words)

    assert isinstance(result, str)


def test_is_noun(word: str) -> None:
    result = is_noun(word)

    assert isinstance(result, bool)


def test_iterative_join(strings: Tuple[str],
                        sep: str) -> None:
    result = iterative_join(*strings,
                            sep=sep)

    assert isinstance(result, collections.Iterator)
