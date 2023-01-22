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
def vectors_of_bools(draw: DrawFn):
    return VectorsOfBools(
        draw(lists(booleans())),
    )


vectors_of_floats = tuples(lists(float32s), lists(float64s)).map(
    lambda vs: VectorsOfFloats(*vs)
)


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


# @composite
# def seq_vectors_of_scalars(draw):
#     return SeqVectorsOfScalars(
#         tuple(draw(lists(booleans()))),
#         tuple(draw(lists(uint8s))),
#         tuple(draw(lists(uint16s))),
#         tuple(draw(lists(uint32s))),
#         tuple(draw(lists(uint64s))),
#         tuple(draw(lists(int8s))),
#         tuple(draw(lists(int16s))),
#         tuple(draw(lists(int32s))),
#         tuple(draw(lists(int64s))),
#         tuple(draw(lists(float32s))),
#         tuple(draw(lists(float64s))),
#     )


@composite
def vectors_of_common1s(draw: DrawFn) -> VectorOfCommon1:
    return VectorOfCommon1(draw(lists(common1s())))


@composite
def vectors_of_optional_common1s(draw):
    return VectorOfOptionalCommon1(draw(lists(common1s()) | none()))


# @composite
# def seq_vectors_of_optional_common1s(draw):
#     return SeqVectorOfOptionalCommon1(draw(lists(common1s()).map(tuple) | none()))


# @composite
# def seq_vectors_of_common1s(draw):
#     return SeqVectorOfCommon1(tuple(draw(lists(common1s()))))


bytearray_tables = binary().map(ByteArrayTable)


vectors_of_enums = lists(sampled_from(ASimpleUByteEnum)).map(VectorOfEnums)
opt_vectors_of_enums = (lists(sampled_from(ASimpleUByteEnum)) | none()).map(
    OptVectorOfEnums
)

# @composite
# def seq_vectors_of_enums(draw):
#     return SeqVectorOfEnums(tuple(draw(lists(sampled_from(ASimpleUByteEnum)))))


optional_bytearray_tables = (binary() | none()).map(OptionalByteArrayTable)

# @composite
# def seq_vectors_of_strings(draw):
#     return SeqVectorOfStrings(tuple(draw(lists(text()))))


vectors_of_strings = lists(text()).map(VectorOfStrings)
optional_vectors_of_strings = (lists(text()) | none()).map(OptionalVectorOfStrings)

# @composite
# def optional_seq_vectors_of_strings(draw):
#     return OptionalSeqVectorOfStrings(draw(lists(text()).map(tuple) | none()))


@given(lists(booleans()).map(VectorsOfBools))
def test_vectors_of_bools(inst: VectorsOfBools):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_floats)
def test_vectors_of_floats(inst: VectorsOfFloats):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_scalars())
def test_vectors_of_scalars_rt(inst: VectorsOfScalars) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(
    tuples(lists(int8s), lists(int16s), lists(int32s), lists(int64s)).map(
        lambda t: VectorsOfInts(*t)
    )
)
def test_vectors_of_ints(inst: VectorsOfInts) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(optional_vectors_of_scalars())
def test_optional_vectors_of_scalars_rt(inst: OptionalVectorsOfScalars) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


# @given(seq_vectors_of_scalars())
# def test_seq_vectors_of_scalars_rt(inst):
#     assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_common1s())
def test_vectors_of_common1s(inst: VectorOfCommon1) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_optional_common1s())
def test_vectors_of_optional_common1s(inst: VectorOfOptionalCommon1):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


# @given(seq_vectors_of_optional_common1s())
# def test_seq_vectors_of_optional_common1s_rt(inst):
#     assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


# @given(seq_vectors_of_common1s())
# def test_seq_vectors_of_common1s_rt(inst):
#     assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(bytearray_tables)
def test_bytearray_tables(inst: ByteArrayTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(optional_bytearray_tables)
def test_optional_bytearray_tables(inst: OptionalByteArrayTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_enums)
def test_vectors_of_enums(inst: VectorOfEnums) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_enums)
def test_vectors_of_enums(inst: VectorOfEnums) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(opt_vectors_of_enums)
def test_opt_vectors_of_enums(inst: OptVectorOfEnums) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


# @given(seq_vectors_of_enums())
# def test_seq_vectors_of_enums(inst):
#     assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


# @given(seq_vectors_of_strings())
# def test_seq_vectors_of_strings(inst):
#     assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_strings)
def test_vectors_of_strings(inst: VectorOfStrings) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(optional_vectors_of_strings)
def test_optional_vectors_of_strings(inst: OptionalVectorOfStrings) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


# @given(optional_seq_vectors_of_strings())
# def test_optional_seq_vectors_of_strings(inst):
#     assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
