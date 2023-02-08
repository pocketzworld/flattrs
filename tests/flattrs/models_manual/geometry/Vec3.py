from __future__ import annotations

from flattr import Float32, flattrs


@flattrs
class Vec3:
    x: Float32
    y: Float32
    z: Float32
