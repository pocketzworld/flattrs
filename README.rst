.. image:: https://travis-ci.org/Tinche/flattrs.svg?branch=master
   :target: https://travis-ci.org/Tinche/flattrs
   :alt: CI Status

Changelog:
----------

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