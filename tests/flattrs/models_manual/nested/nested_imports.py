from __future__ import annotations

from flattr import flattrs

from ..common import Common1
from ..geometry.Vec3 import Vec3


@flattrs
class NestedInclude:
    test: Vec3 | None = None
    common: Common1 | None = None
