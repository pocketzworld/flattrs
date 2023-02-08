"""Compare the flatc and flattrs implementations."""
from attrs import asdict
from hypothesis import given
from hypothesis.strategies import text, tuples

from flattr import model_from_bytes, model_to_bytes

from ..flatc import models_common as models_common_flatc
from ..flatc.test_common import all_scalars, all_scalars_with_defaults
from ..flattrs.models import common as models_common_flattrs
from ..strats import int32s, uint8s


@given(
    tuples(text(), uint8s, int32s).map(
        lambda a: (models_common_flatc.Common1(*a), models_common_flattrs.Common1(*a))
    )
)
def test_common1(
    insts: tuple[models_common_flatc.Common1, models_common_flattrs.Common1]
) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = model_to_bytes(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flattrs_bytes)) == asdict(
        model_from_bytes(flattrs.__class__, flatc_bytes)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        model_from_bytes(flattrs.__class__, flatc_bytes)
    )


@given(all_scalars().map(lambda s: (s, models_common_flattrs.AllScalars(**asdict(s)))))
def test_all_scalars(
    insts: tuple[models_common_flatc.AllScalars, models_common_flattrs.AllScalars]
) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = model_to_bytes(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flattrs_bytes)) == asdict(
        model_from_bytes(flattrs.__class__, flatc_bytes)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        model_from_bytes(flattrs.__class__, flatc_bytes)
    )


@given(
    all_scalars_with_defaults().map(
        lambda s: (s, models_common_flattrs.AllScalarsWithDefaults(**asdict(s)))
    )
)
def test_all_scalars_with_defaults(
    insts: tuple[
        models_common_flatc.AllScalarsWithDefaults,
        models_common_flattrs.AllScalarsWithDefaults,
    ]
) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = model_to_bytes(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flattrs_bytes)) == asdict(
        model_from_bytes(flattrs.__class__, flatc_bytes)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        model_from_bytes(flattrs.__class__, flatc_bytes)
    )
