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

from flattr import dumps, loads

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
from .models.enums import ASimpleUByteEnum
from .models.vectors import (
    ByteArrayTable,
    OptionalByteArrayTable,
    OptionalVectorOfStrings,
    OptionalVectorsOfScalars,
    OptVectorOfEnums,
    VectorOfCommon1,
    VectorOfEnums,
    VectorOfOptionalCommon1,
    VectorOfStrings,
    VectorsOfBools,
    VectorsOfFloats,
    VectorsOfInts,
    VectorsOfScalars,
)
from .test_common import common1s


@composite
def vectors_of_scalars(draw: DrawFn) -> VectorsOfScalars:
    return VectorsOfScalars(
        draw(lists(booleans())),
        draw(binary()),
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
        draw(binary() | none()),
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


@given(lists(booleans()).map(VectorsOfBools))
def test_vectors_of_bools(inst: VectorsOfBools) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(tuples(lists(float32s), lists(float64s)).map(lambda vs: VectorsOfFloats(*vs)))
def test_vectors_of_floats(inst: VectorsOfFloats) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(vectors_of_scalars())
def test_vectors_of_scalars(inst: VectorsOfScalars) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(
    tuples(lists(int8s), lists(int16s), lists(int32s), lists(int64s)).map(
        lambda t: VectorsOfInts(*t)
    )
)
def test_vectors_of_ints(inst: VectorsOfInts) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(optional_vectors_of_scalars())
def test_optional_vectors_of_scalars(inst: OptionalVectorsOfScalars) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(vectors_of_common1s())
def test_vectors_of_common1s(inst: VectorOfCommon1) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(vectors_of_optional_common1s())
def test_vectors_of_optional_common1s(inst: VectorOfOptionalCommon1):
    assert inst == loads(dumps(inst), inst.__class__)


@given(bytearray_tables)
def test_bytearray_tables(inst: ByteArrayTable) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given((binary() | none()).map(OptionalByteArrayTable))
def test_optional_bytearray_tables(inst: OptionalByteArrayTable) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(lists(sampled_from(ASimpleUByteEnum)).map(VectorOfEnums))
def test_vectors_of_enums(inst: VectorOfEnums) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given((lists(sampled_from(ASimpleUByteEnum)) | none()).map(OptVectorOfEnums))
def test_opt_vectors_of_enums(inst: OptVectorOfEnums) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(lists(text()).map(VectorOfStrings))
def test_vectors_of_strings(inst: VectorOfStrings) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given((lists(text()) | none()).map(OptionalVectorOfStrings))
def test_optional_vectors_of_strings(inst: OptionalVectorOfStrings) -> None:
    assert inst == loads(dumps(inst), inst.__class__)
