from __future__ import annotations

from attrs import define

from flattr import Float32


@define
class Vec3:
    x: Float32
    y: Float32
    z: Float32
