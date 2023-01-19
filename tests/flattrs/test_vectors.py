from hypothesis import given
from hypothesis.strategies import (
    DrawFn,
    binary,
    booleans,
    composite,
    lists,
    none,
    sampled_from,
    text,
    tuples,
)

from flattr import model_from_bytes, model_to_bytes

from ..strats import (
    float32s,
    float64s,
    int8s,
    int16s,
    int32s,
    int64s,
    uint8s,
    uint16s,
    uint32s,
    uint64s,
)
from .models_enums import ASimpleUByteEnum
from .models_vectors import (
    ByteArrayTable,
    OptionalByteArrayTable,
    OptionalVectorsOfScalars,
    VectorOfCommon1,
    VectorOfEnums,
    VectorOfOptionalCommon1,
    VectorsOfBools,
    VectorsOfInts,
    VectorsOfScalars,
)
from .test_common import common1s


@given(lists(booleans()).map(VectorsOfBools))
def test_vectors_of_bools(inst: VectorsOfBools):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@composite
def vectors_of_scalars(draw: DrawFn) -> VectorsOfScalars:
    return VectorsOfScalars(
        draw(lists(booleans())),
        draw(lists(uint8s)),
        draw(lists(uint16s)),
        draw(lists(uint32s)),
        draw(lists(uint64s)),
        draw(lists(int8s)),
        draw(lists(int16s)),
        draw(lists(int32s)),
        draw(lists(int64s)),
        draw(lists(float32s)),
        draw(lists(float64s)),
    )


@composite
def optional_vectors_of_scalars(draw):
    return OptionalVectorsOfScalars(
        draw(lists(booleans()) | none()),
        draw(lists(uint8s) | none()),
        draw(lists(uint16s) | none()),
        draw(lists(uint32s) | none()),
        draw(lists(uint64s) | none()),
        draw(lists(int8s) | none()),
        draw(lists(int16s) | none()),
        draw(lists(int32s) | none()),
        draw(lists(int64s) | none()),
        draw(lists(float32s) | none()),
        draw(lists(float64s) | none()),
    )


@composite
def vectors_of_common1s(draw: DrawFn) -> VectorOfCommon1:
    return VectorOfCommon1(draw(lists(common1s)))


@composite
def vectors_of_optional_common1s(draw):
    return VectorOfOptionalCommon1(draw(lists(common1s) | none()))


bytearray_tables = binary().map(ByteArrayTable)


@given(vectors_of_scalars())
def test_vectors_of_scalars_rt(inst: VectorsOfScalars):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(
    tuples(lists(int8s), lists(int16s), lists(int32s), lists(int64s)).map(
        lambda t: VectorsOfInts(*t)
    )
)
def test_vectors_of_ints(inst: VectorsOfInts) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(optional_vectors_of_scalars())
def test_optional_vectors_of_scalars(inst: OptionalVectorsOfScalars) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_common1s())
def test_vectors_of_common1s_rt(inst: VectorOfCommon1) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_optional_common1s())
def test_vectors_of_optional_common1s_rt(inst: VectorOfOptionalCommon1):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(bytearray_tables)
def test_bytearray_tables(inst: ByteArrayTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given((binary() | none()).map(OptionalByteArrayTable))
def test_optional_bytearray_tables(inst: OptionalByteArrayTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(lists(sampled_from(ASimpleUByteEnum)).map(VectorOfEnums))
def test_vectors_of_enums(inst: VectorOfEnums) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
