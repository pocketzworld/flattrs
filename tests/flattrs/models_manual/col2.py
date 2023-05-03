from __future__ import annotations

from attrs import define

from .collisions.Ns2 import Collision


@define
class CollidingTables2:
    ns1: Collision
