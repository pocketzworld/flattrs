from flattr import flattrs

from .models_common import Common1


@flattrs
class ContainsTable:
    inner: Common1


@flattrs
class OptionalTable:
    inner: Common1 | None
