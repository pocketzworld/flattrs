from __future__ import annotations

from attrs import define

from .collisions.Ns1 import Collision


@define
class CollidingTables:
    ns1: Collision
