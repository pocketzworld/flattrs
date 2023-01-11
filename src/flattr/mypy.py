from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_define_makers

# This work just like @attrs.define
attr_define_makers.add("flattr.Flatbuffer")
attr_define_makers.add("flattr.from_package")


class MyPlugin(Plugin):
    # Our plugin does nothing but it has to exist so this file gets loaded.
    pass


def plugin(version):
    return MyPlugin
