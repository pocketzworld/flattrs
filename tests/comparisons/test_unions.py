"""Compare the flatc and flattrs implementations."""
from attrs import asdict
from cattrs import structure, unstructure
from hypothesis import given

from flattr import model_from_bytes, model_to_bytes

from ..flatc import models_unions as models_unions_flatc
from ..flatc.test_unions import unions_of_nested_tables
from ..flattrs import models_unions as models_unions_flattrs


@given(
    unions_of_nested_tables().map(
        lambda t: (
            t,
            structure(unstructure(t), models_unions_flattrs.UnionOfNestedTables),
        )
    )
)
def test_union_of_nested_tables(
    insts: tuple[
        models_unions_flatc.UnionOfNestedTables,
        models_unions_flattrs.UnionOfNestedTables,
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
