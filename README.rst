.. image:: https://img.shields.io/github/license/pocketzworld/flattrs?style=flat-square
   :alt: MIT

Changelog:
----------

23.1.0b9 (2023-05-17)
~~~~~~~~~~~~~~~~~~~~~
* Set the minimum _attrs_ version to ensure we get the right `attrs.resolve_types`.

23.1.0b8 (2023-05-03)
~~~~~~~~~~~~~~~~~~~~~
* Greatly improve namespace handling.

23.1.0b7 (2023-03-28)
~~~~~~~~~~~~~~~~~~~~~
* Implement reordering of unions in the generated code where required.
* Internal refactor for more immutability.

23.1.0b6 (2023-03-15)
~~~~~~~~~~~~~~~~~~~~~
* Add special support for unions of a single class.

23.1.0b5 (2023-03-08)
~~~~~~~~~~~~~~~~~~~~~
* Drop Python 3.9 support.
* A complete rewrite.

0.1.16 (2023-01-19)
~~~~~~~~~~~~~~~~~~~
* Update the underlying `flatbuffers` dependency.
* Switch to using `attrs.define` under the hood, allowing the use of next-gen _attrs_ APIs.

0.1.15 (2022-12-16)
~~~~~~~~~~~~~~~~~~~
* Include Python 3.11.

0.1.14 (2022-06-21)
~~~~~~~~~~~~~~~~~~~
* Add dataclass transform support.
* Include Python 3.10, remove 3.6, 3.7 and 3.8.

0.1.13 (2021-02-12)
~~~~~~~~~~~~~~~~~~~
* Add support for optional vectors and sequences of strings.

0.1.12 (2021-02-11)
~~~~~~~~~~~~~~~~~~~
* Fix code generation bug.

0.1.11 (2021-02-11)
~~~~~~~~~~~~~~~~~~~
* Add support for optional vectors and sequences of tables.

0.1.10 (2021-01-26)
~~~~~~~~~~~~~~~~~~~
* Add support for optional vectors of scalars.

0.1.9 (2020-11-10)
~~~~~~~~~~~~~~~~~~
* Add support for `typing.Sequence[str]` (deserializes to tuples).

0.1.8 (2020-10-15)
~~~~~~~~~~~~~~~~~~
* Add support for `typing.Sequence[T]` (deserializes to tuples).
* Python 3.9 support.

0.1.7 (2020-04-28)
~~~~~~~~~~~~~~~~~~
* `flattr.from_package`, `Flatbuffer.from_package` and `Flatbuffer` now accept `repr`.

0.1.6 (2020-04-16)
~~~~~~~~~~~~~~~~~~
* `flattr.from_package`, `flattr.from_package_enum`, `Flatbuffer.from_package` and `FlatbufferEnum.from_package` convenience aliases.
* Include `py.typed` for Mypy to pick up.
* Drop Python 3.5 support.
* Bundle the Mypy plugin. (Configure Mypy to load `flattr.mypy`.)

0.1.5 (2020-01-03)
~~~~~~~~~~~~~~~~~~
* 3.7 and 3.8 support.

0.1.4 (2019-10-23)
~~~~~~~~~~~~~~~~~~
* Support optional unions.

0.1.3 (2019-06-18)
~~~~~~~~~~~~~~~~~~
* Support lists of int enums.

0.1.2 (2019-01-31)
~~~~~~~~~~~~~~~~~~
* Fixed an issue with unions of tables from another namespace.
* Removed spurious print when serializing byte arrays.

0.1.1 (2018-09-21)
~~~~~~~~~~~~~~~~~~
* Fixed an issue with union classes.