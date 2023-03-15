from pathlib import Path

import click

from .renderer import render


@click.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
@click.option("--gen-namespace-exports/--no-gen-namespace-exports", default=False)
def main(input: Path, output: Path, gen_namespace_exports: bool) -> None:
    render(input, output, gen_namespace_exports)


if __name__ == "__main__":
    main()
