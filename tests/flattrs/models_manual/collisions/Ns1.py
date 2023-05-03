from __future__ import annotations

from attrs import define

from flattrs import Float32


@define
class Collision:
    x: Float32
