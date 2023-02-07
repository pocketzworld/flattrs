from pathlib import Path
from subprocess import run

from flattr.modgen.renderer import render


def assert_dirs_identical(dir_a: Path, dir_b: Path) -> None:
    assert dir_a.is_dir()
    assert dir_b.is_dir()
    list_a = [
        p.relative_to(dir_a) for p in dir_a.glob("*") if p.name not in ("__pycache__")
    ]
    list_b = [
        p.relative_to(dir_b) for p in dir_b.glob("*") if p.name not in ("__pycache__")
    ]
    assert list_a == list_b

    for elem_a, elem_b in zip(list_a, list_b):
        file_a = dir_a / elem_a
        file_b = dir_b / elem_b
        if file_a.is_file():
            assert file_b.is_file()
            assert file_a.read_bytes() == file_b.read_bytes()
        else:
            assert not file_b.is_file()


def test_compare_to_manual(tmp_path: Path) -> None:
    """The manually inspected models are in ./flattrs/models_manual.

    These should be identical to generated models.
    """
    dest_dir = tmp_path / "models"
    render(Path(__file__).parent / "flatbufferdefs", dest_dir)
    run(["isort", str(dest_dir)], check=True)
    run(["black", str(dest_dir)], check=True)
    assert_dirs_identical(Path(__file__).parent / "flattrs" / "models_manual", dest_dir)