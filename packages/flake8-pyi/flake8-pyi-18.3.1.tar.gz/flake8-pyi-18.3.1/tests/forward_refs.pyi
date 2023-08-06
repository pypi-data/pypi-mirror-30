from typing import Optional, Union


MaybeCStr = Optional[CStr]
CStr = Union[C, str]
__version__ = ...  # type: str
__author__ = ...  # type: str


def make_default_c() -> C:
    ...


class D(C):
    parent = None  # type: C

    def __init__(self) -> None:
        ...


class C:
    other = None  # type: C

    def __init__(self) -> None:
        ...

    def from_str(self, s: str) -> C:
        ...
