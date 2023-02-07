from configparser import ConfigParser
from pathlib import Path

import click

from .renderer import render


@click.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
def main(input: Path, output: Path) -> None:
    config = ConfigParser()
    excluded = set()
    frozen = set()
    no_repr = set()
    try:
        with (Path("conf.ini")).open() as f:
            config.read_string(f.read())
        excluded = set(e.strip() for e in config.get("flattrs", "exclude").split(","))
        frozen = set(e.strip() for e in config.get("flattrs", "frozen").split(","))
        no_repr = set(e.strip() for e in config.get("flattrs", "no_repr").split(","))
    except FileNotFoundError:
        pass

    no_repr_per_class = {}
    for cls_and_attr in no_repr:
        cls, attr = cls_and_attr.split(".", 1)
        no_repr_per_class.setdefault(cls, set()).add(attr)

    render(input, output)


if __name__ == "__main__":
    main()