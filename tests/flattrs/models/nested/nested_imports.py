from __future__ import annotations

from flattr import flattrs

from ..geometry.Vec3 import Vec3


@flattrs
class NestedInclude:
    test: Vec3 | None
