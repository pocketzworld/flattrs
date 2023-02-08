"""Test serialization and deserialization of enums."""
from hypothesis import given
from hypothesis.strategies import sampled_from, tuples

from flattr import model_from_bytes, model_to_bytes

from .models.enums import (
    AllEnums,
    AnInt8Enum,
    AnInt16Enum,
    AnInt32Enum,
    AnInt64Enum,
    AnUInt8Enum,
    AnUInt16Enum,
    AnUInt32Enum,
    AnUInt64Enum,
    ASimpleByteEnum,
    ASimpleUByteEnum,
)

all_enums = tuples(
    sampled_from(ASimpleUByteEnum),
    sampled_from(ASimpleByteEnum),
    sampled_from(AnUInt8Enum),
    sampled_from(AnInt8Enum),
    sampled_from(AnUInt16Enum),
    sampled_from(AnInt16Enum),
    sampled_from(AnUInt32Enum),
    sampled_from(AnInt32Enum),
    sampled_from(AnUInt64Enum),
    sampled_from(AnInt64Enum),
).map(lambda t: AllEnums(*t))


@given(all_enums)
def test_all_enums(inst: AllEnums) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
