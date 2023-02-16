from __future__ import annotations

from attrs import define

from .geometry.Vec3 import Vec3


@define
class Includes:
    vec3: Vec3
