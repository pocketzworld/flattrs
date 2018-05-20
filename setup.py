from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="flattrs",
    version="0.1",
    install_requires=["attrs", "flatbuffers==20180424161048"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    dependency_links=[
        "git+https://github.com/google/flatbuffers@v1.9.0#egg=flatbuffers-20180424161048&subdirectory=python"
    ],
    ext_modules=cythonize("src/flattr/cflattr/*.pyx", annotate=True),
    zip_safe=False,
    extras_require={"dev": ["pytest", "hypothesis"]},
)
