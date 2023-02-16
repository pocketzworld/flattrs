from types import GenericAlias, UnionType
from typing import Any, TypeVar, Union, _AnnotatedAlias, _GenericAlias, get_args

from attr._make import _obj_setattr
from attrs import fields

from ._consts import NoneType
from ._types import Optionality

T = TypeVar("T")


def is_subclass(typ, supertype) -> bool:
    """A safe version of `is_subclass`."""
    try:
        return issubclass(typ, supertype)
    except TypeError:
        return False


def is_generic_subclass(t, s):
    return (isinstance(t, _GenericAlias) and t.__origin__ is s) or (
        isinstance(t, GenericAlias) and t.__origin__ is s
    )


def get_annotation_and_base(typ, annotation_cls: type[T]) -> tuple[T, Any] | None:
    if typ.__class__ is _AnnotatedAlias:
        args = get_args(typ)
        for arg in args[1:]:
            if isinstance(arg, annotation_cls):
                return arg, args[0]
    return None


def get_optional_arg(type) -> Any | None:
    """Is this annotation an `Optional` (union of something and None)?"""
    if getattr(type, "__origin__", None) is Union or type.__class__ is UnionType:
        union_args = type.__args__
        if len(union_args) == 2 and NoneType in union_args:
            return [a for a in union_args if a is not None][0]

    return None


def get_union_args(type) -> tuple[type, ...] | None:
    """Is this annotation a Union?"""
    if getattr(type, "__origin__", None) is Union or type.__class__ is UnionType:
        return type.__args__

    return None


def get_list_args(type) -> tuple[Any, Optionality] | None:
    """Is this type annotation a list of something?"""
    optional = False
    if (o := get_optional_arg(type)) is not None:
        optional = True
        type = o
    if is_generic_subclass(type, list):
        arg = get_args(type)[0]
        return arg, optional
    return None


def resolve_types(cls, globalns=None, localns=None, attribs=None, include_extras=True):
    # Since calling get_type_hints is expensive we cache whether we've
    # done it already.
    if getattr(cls, "__attrs_types_resolved__", None) != cls:
        import typing

        kwargs = {
            "globalns": globalns,
            "localns": localns,
            "include_extras": include_extras,
        }

        hints = typing.get_type_hints(cls, **kwargs)
        for field in fields(cls) if attribs is None else attribs:
            if field.name in hints:
                # Since fields have been frozen we must work around it.
                _obj_setattr(field, "type", hints[field.name])
        # We store the class we resolved so that subclasses know they haven't
        # been resolved.
        cls.__attrs_types_resolved__ = cls

    # Return the class so you can use it as a decorator too.
    return cls
