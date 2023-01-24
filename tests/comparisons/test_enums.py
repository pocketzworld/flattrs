"""Compare the flatc and flattrs implementations."""
from attrs import asdict
from cattrs import structure, unstructure
from hypothesis import given

from flattr import model_from_bytes, model_to_bytes

from ..flatc import models_enums as models_enums_flatc
from ..flatc.test_enums import all_enums
from ..flattrs import models_enums as models_enums_flattrs


@given(
    all_enums.map(
        lambda t: (t, structure(unstructure(t), models_enums_flattrs.AllEnums))
    )
)
def test_all_enums(
    insts: tuple[
        models_enums_flatc.AllEnums,
        models_enums_flattrs.AllEnums,
    ]
):
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