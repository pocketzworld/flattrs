from attrs import asdict
from cattrs import structure, unstructure
from hypothesis import given
from hypothesis.strategies import booleans, lists, tuples

from flattr import dumps, loads
from tests import model_from_bytes, model_to_bytes

from ..flatc import models_vectors as models_vectors_flatc
from ..flatc.test_vectors import (
    bytearray_tables,
    optional_bytearray_tables,
    optional_vectors_of_scalars,
    optional_vectors_of_strings,
    vectors_of_common1s,
    vectors_of_enums,
    vectors_of_floats,
    vectors_of_optional_common1s,
    vectors_of_scalars,
    vectors_of_strings,
)
from ..flattrs.models import vectors as models_vectors_flattrs
from ..strats import int8s, int16s, int32s, int64s


@given(
    lists(booleans()).map(
        lambda v: (
            models_vectors_flatc.VectorsOfBools(v),
            models_vectors_flattrs.VectorsOfBools(v),
        )
    )
)
def test_vectors_of_bools(
    insts: tuple[
        models_vectors_flatc.VectorsOfBools, models_vectors_flattrs.VectorsOfBools
    ]
):
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
    vectors_of_floats.map(
        lambda v: (v, structure(unstructure(v), models_vectors_flattrs.VectorsOfFloats))
    )
)
def test_vectors_of_floats(
    insts: tuple[
        models_vectors_flatc.VectorsOfFloats, models_vectors_flattrs.VectorsOfFloats
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
    tuples(lists(int8s), lists(int16s), lists(int32s), lists(int64s)).map(
        lambda t: (
            models_vectors_flatc.VectorsOfInts(*t),
            models_vectors_flattrs.VectorsOfInts(*t),
        )
    )
)
def test_vectors_of_ints(
    insts: tuple[
        models_vectors_flatc.VectorsOfInts, models_vectors_flattrs.VectorsOfInts
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    vectors_of_scalars().map(
        lambda v: (v, models_vectors_flattrs.VectorsOfScalars(**asdict(v)))
    )
)
def test_vectors_of_scalars(
    insts: tuple[
        models_vectors_flatc.VectorsOfScalars, models_vectors_flattrs.VectorsOfScalars
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    optional_vectors_of_scalars().map(
        lambda v: (v, models_vectors_flattrs.OptionalVectorsOfScalars(**asdict(v)))
    )
)
def test_vectors_of_scalars(
    insts: tuple[
        models_vectors_flatc.OptionalVectorsOfScalars,
        models_vectors_flattrs.OptionalVectorsOfScalars,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    vectors_of_common1s().map(
        lambda v: (v, structure(unstructure(v), models_vectors_flattrs.VectorOfCommon1))
    )
)
def test_vectors_of_common1(
    insts: tuple[
        models_vectors_flatc.VectorOfCommon1,
        models_vectors_flattrs.VectorOfCommon1,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    vectors_of_optional_common1s().map(
        lambda v: (
            v,
            structure(unstructure(v), models_vectors_flattrs.VectorOfOptionalCommon1),
        )
    )
)
def test_vectors_of_opt_common1(
    insts: tuple[
        models_vectors_flatc.VectorOfOptionalCommon1,
        models_vectors_flattrs.VectorOfOptionalCommon1,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    bytearray_tables.map(
        lambda v: (
            v,
            structure(unstructure(v), models_vectors_flattrs.ByteArrayTable),
        )
    )
)
def test_bytearray_tables(
    insts: tuple[
        models_vectors_flatc.ByteArrayTable,
        models_vectors_flattrs.ByteArrayTable,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    optional_bytearray_tables.map(
        lambda v: (
            v,
            structure(unstructure(v), models_vectors_flattrs.OptionalByteArrayTable),
        )
    )
)
def test_opt_bytearray_tables(
    insts: tuple[
        models_vectors_flatc.OptionalByteArrayTable,
        models_vectors_flattrs.OptionalByteArrayTable,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    vectors_of_enums.map(
        lambda v: (
            v,
            structure(unstructure(v), models_vectors_flattrs.VectorOfEnums),
        )
    )
)
def test_vectors_of_enums(
    insts: tuple[
        models_vectors_flatc.VectorOfEnums,
        models_vectors_flattrs.VectorOfEnums,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    vectors_of_strings.map(
        lambda v: (
            v,
            structure(unstructure(v), models_vectors_flattrs.VectorOfStrings),
        )
    )
)
def test_vectors_of_strings(
    insts: tuple[
        models_vectors_flatc.VectorOfStrings,
        models_vectors_flattrs.VectorOfStrings,
    ]
):
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )


@given(
    optional_vectors_of_strings.map(
        lambda v: (
            v,
            structure(unstructure(v), models_vectors_flattrs.OptionalVectorOfStrings),
        )
    )
)
def test_opt_vectors_of_strings(
    insts: tuple[
        models_vectors_flatc.OptionalVectorOfStrings,
        models_vectors_flattrs.OptionalVectorOfStrings,
    ]
) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flatc_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flatc_bytes, flattrs.__class__)
    )
