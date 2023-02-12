from __future__ import annotations

from attrs import define

from ..common import Common1
from ..geometry.Vec3 import Vec3


@define
class NestedInclude:
    test: Vec3 | None = None
    common: Common1 | None = None
