from __future__ import annotations

from attrs import define


@define
class OnlyString:
    str: str


@define
class OnlyString2:
    str: str


EarlyUnion = OnlyString | OnlyString2


@define
class OnlyStringAfterUnion:
    onlyString: EarlyUnion
