"""Compare the flatc and flattrs implementations."""
from attrs import asdict
from hypothesis import given
from hypothesis.strategies import binary, integers, just, text

from flattr import dumps, loads, model_from_bytes, model_to_bytes

from ..flatc import models_enums as models_enums_flatc
from ..flatc import models_trivial as models_trivial_flatc
from ..flatc.models_trivial import HasCaps, JustAnOptionalString, JustAString, JustBytes
from ..flattrs.models import trivial as models_trivial_flattrs
from ..flattrs.models.trivial import HasCaps as HasCapsFlattrs
from ..flattrs.models.trivial import JustAnOptionalString as JustAnOptionalStringFlattrs
from ..flattrs.models.trivial import JustAString as JustAStringFlattrs
from ..flattrs.models.trivial import JustBytes as JustBytesFlattrs
from ..strats import float32s, float64s


@given(text().map(lambda t: (JustAString(t), JustAStringFlattrs(t))))
def test_just_string(insts: tuple[JustAString, JustAStringFlattrs]):
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
    (text() | just(None)).map(
        lambda t: (JustAnOptionalString(t), JustAnOptionalStringFlattrs(t))
    )
)
def test_just_optional_string(
    insts: tuple[JustAnOptionalString, JustAnOptionalStringFlattrs]
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


@given(binary().map(lambda t: (JustBytes(t), JustBytes(t))))
def test_just_bytes(insts: tuple[JustBytes, JustBytesFlattrs]) -> None:
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
    (binary() | just(None)).map(
        lambda t: (
            models_trivial_flatc.JustOptionalBytes(t),
            models_trivial_flattrs.JustOptionalBytes(t),
        )
    )
)
def test_just_opt_bytes(
    insts: tuple[
        models_trivial_flatc.JustOptionalBytes, models_trivial_flattrs.JustOptionalBytes
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
    float32s.map(
        lambda t: (
            models_trivial_flatc.JustAFloat(t),
            models_trivial_flattrs.JustAFloat(t),
        )
    )
)
def test_just_floats(
    insts: tuple[models_trivial_flatc.JustAFloat, models_trivial_flattrs.JustAFloat]
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


# @given(
#     float32s.map(
#         lambda t: (
#             models_trivial_flatc.JustAFloat(t),
#             models_trivial_flattrs.JustAFloatAnnotated(t),
#         )
#     )
# )
# def test_just_floats_annotated(
#     insts: tuple[
#         models_trivial_flatc.JustAFloat, models_trivial_flattrs.JustAFloatAnnotated
#     ]
# ):
#     flatc, flattrs = insts
#     flatc_bytes = model_to_bytes(flatc)
#     flattrs_bytes = model_to_bytes(flattrs)
#     assert flatc_bytes == flattrs_bytes

#     assert asdict(model_from_bytes(flatc.__class__, flattrs_bytes)) == asdict(
#         model_from_bytes(flattrs.__class__, flatc_bytes)
#     )


@given(
    float64s.map(
        lambda t: (
            models_trivial_flatc.JustADouble(t),
            models_trivial_flattrs.JustADouble(t),
        )
    )
)
def test_just_doubles(
    insts: tuple[models_trivial_flatc.JustADouble, models_trivial_flattrs.JustADouble]
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
    integers(min_value=0, max_value=len(models_enums_flatc.ASimpleByteEnum) - 1).map(
        lambda enum_ix: (
            models_trivial_flatc.JustAnEnum(
                list(models_enums_flatc.ASimpleByteEnum)[enum_ix]
            ),
            models_trivial_flattrs.JustAnEnum(
                list(models_enums_flatc.ASimpleByteEnum)[enum_ix]
            ),
        )
    )
)
def test_just_byte_enums(
    insts: tuple[models_trivial_flatc.JustAnEnum, models_trivial_flattrs.JustAnEnum]
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


@given(text().map(lambda t: (HasCaps(t, t, t), HasCapsFlattrs(t, t, t))))
def test_has_caps(insts: tuple[HasCaps, HasCapsFlattrs]) -> None:
    flatc, flattrs = insts
    flatc_bytes = model_to_bytes(flatc)
    flattrs_bytes = dumps(flattrs)
    assert flatc_bytes == flattrs_bytes

    assert asdict(model_from_bytes(flatc.__class__, flatc_bytes)) == asdict(
        loads(flattrs_bytes, flattrs.__class__)
    )

    assert repr(model_from_bytes(flatc.__class__, flatc_bytes)) == repr(
        loads(flattrs_bytes, flattrs.__class__)
    )
