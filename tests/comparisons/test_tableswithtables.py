"""Compare the flatc and flattrs implementations."""
from attrs import asdict
from cattrs import structure, unstructure
from hypothesis import given

from flattr import model_from_bytes, model_to_bytes

from ..flatc import models_tableswithtables as models_tableswithtables_flatc
from ..flatc.test_tableswithtables import contains_tables, optional_tables
from ..flattrs import models_tableswithtables as models_tableswithtables_flattrs


@given(
    contains_tables().map(
        lambda i: (
            i,
            structure(unstructure(i), models_tableswithtables_flattrs.ContainsTable),
        )
    )
)
def test_contains_table(
    insts: tuple[
        models_tableswithtables_flatc.ContainsTable,
        models_tableswithtables_flattrs.ContainsTable,
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


@given(
    optional_tables.map(
        lambda i: (
            i,
            structure(unstructure(i), models_tableswithtables_flattrs.OptionalTable),
        )
    )
)
def test_optional_table(
    insts: tuple[
        models_tableswithtables_flatc.OptionalTable,
        models_tableswithtables_flattrs.OptionalTable,
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
