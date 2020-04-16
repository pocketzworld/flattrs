from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_class_makers

# This work just like attr.s i.e. it has the same defaults as attr.s
attr_class_makers.add("flattr.Flatbuffer")
attr_class_makers.add("flattr.from_package")


class MyPlugin(Plugin):
    # Our plugin does nothing but it has to exist so this file gets loaded.
    pass


def plugin(version):
    return MyPlugin
