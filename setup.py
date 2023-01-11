from platform import python_implementation

from setuptools import find_packages, setup

if python_implementation() != "PyPy":
    from Cython.Build import cythonize

    ext_modules = cythonize("src/flattr/cflattr/*.pyx", annotate=True)
else:
    ext_modules = []

setup(
    name="flattrs",
    version="0.1.16b5",
    install_requires=["attrs", "flatbuffers==23.1.4", "numpy"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=ext_modules,
    zip_safe=False,
    extras_require={
        "dev": [
            "pytest",
            "hypothesis==6.61.0",
            "cython==0.29.32",
            "coverage",
            "tox==4.0.11",
        ]
    },
    package_data={"": ["*.pxd", "*.pyx", "py.typed"]},
    license="MIT license",
)
