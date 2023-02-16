from enum import unique
from importlib import import_module
from sys import modules
from typing import TypeVar

from attrs import define

from ._flatc import (
    UNION_CL,
    _make_fb_functions,
    get_num_slots_from_flatc_module,
    get_scalar_list_types,
    get_scalar_types,
    get_union_mapping_overrides,
    make_from_bytes_fn,
    make_from_fb_fn,
)

try:
    from flattr.cflattr.builder import Builder
except ImportError:
    from flatbuffers.builder import Builder


def Flatbuffer(fb_cl, frozen: bool = False, repr: bool = True):
    def wrapper(cl):
        res = define(slots=True, frozen=frozen, repr=repr)(cl)
        res.__fb_module__ = modules[fb_cl.__module__]
        res.__fb_class__ = fb_cl
        num_slots = get_num_slots_from_flatc_module(res.__fb_module__)
        scalars = get_scalar_types(res, res.__fb_module__)
        scalar_list_overrides = get_scalar_list_types(res)
        union_overrides = get_union_mapping_overrides(res)
        _make_fb_functions(
            res,
            num_slots=num_slots,
            make_from_bytes_fn=make_from_bytes_fn,
            make_from_fb_fn=make_from_fb_fn,
            field_overrides=scalars,
            scalar_list_overrides=scalar_list_overrides,
            union_overrides=union_overrides,
        )

        return res

    return wrapper


def FlatbufferEnum(fb_cl):
    def wrapper(cl):
        res = unique(cl)
        res.__fb_module__ = modules[fb_cl.__module__]
        res.__fb_class__ = fb_cl

        if cl.__name__ != fb_cl.__name__:
            raise ValueError(f"Names don't match: {cl.__name__}/{fb_cl.__name__}.")

        for member in cl:
            if (
                not hasattr(fb_cl, member.name)
                or getattr(fb_cl, member.name) != member.value
            ):
                raise ValueError(f"{cl}/{member.name} doesn't match {fb_cl}.")

        return res

    return wrapper


def from_package(pkg, frozen: bool = False, repr: bool = True):
    def wrap_cls(cl):
        cl_name = cl.__name__
        module = import_module(f"{pkg.__package__}.{cl_name}")
        fb_cl = getattr(module, cl_name)
        return Flatbuffer(fb_cl, frozen=frozen, repr=repr)(cl)

    return wrap_cls


def from_package_enum(pkg):
    def wrap_cls(cl):
        cl_name = cl.__name__
        module = import_module(f"{pkg.__package__}.{cl_name}")
        fb_cl = getattr(module, cl_name)
        return FlatbufferEnum(fb_cl)(cl)

    return wrap_cls


Flatbuffer.from_package = from_package
FlatbufferEnum.from_package = from_package_enum


def model_to_bytes(inst, builder: Builder | None = None) -> bytes:
    builder = Builder(10000) if builder is None else builder
    string_offsets = {}
    node_offsets = {}

    offset = inst.__fb_add_to_builder__(builder, string_offsets, node_offsets)

    builder.Finish(offset)  # Last offset.
    return bytes(builder.Output())


_T = TypeVar("_T")


def model_from_bytes(cl: type[_T], payload: bytes) -> _T:
    """Deserialize an instance of `cl` from the given payload."""
    return cl.__fb_from_bytes__(payload)
