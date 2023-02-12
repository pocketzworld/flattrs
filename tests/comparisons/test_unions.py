"""Compare the flatc and flattrs implementations."""
from attrs import asdict
from cattrs import structure, unstructure
from hypothesis import given

from flattr import dumps, loads, model_from_bytes, model_to_bytes

from ..flatc import models_unions as models_unions_flatc
from ..flatc.test_unions import numbered_union_tables, unions_of_nested_tables
from ..flattrs.models import common as models_common_flattrs
from ..flattrs.models import tableswithtables as models_unions_flattrs


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
) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flattrs_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    numbered_union_tables().map(
        lambda t: (
            t,
            models_unions_flattrs.NumberedUnionTable(
                structure(
                    unstructure(t)["innerUnion"],
                    {
                        "AllScalars": models_common_flattrs.AllScalars,
                        "AllScalarsWithDefaults": models_common_flattrs.AllScalarsWithDefaults,
                        "Common1": models_common_flattrs.Common1,
                        "NoneType": None,
                    }[t.innerUnion.__class__.__name__],
                )
            ),
        ),
    )
)
def test_numbered_union_tables(
    insts: tuple[
        models_unions_flatc.NumberedUnionTable,
        models_unions_flattrs.NumberedUnionTable,
    ]
) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flattrs_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )
