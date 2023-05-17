from platform import python_implementation

from setuptools import find_packages, setup

if python_implementation() != "PyPy":
    from Cython.Build import cythonize

    ext_modules = cythonize("src/flattrs/cflattrs/*.pyx", annotate=True)
else:
    ext_modules = []

setup(
    name="flattrs",
    long_description="Flatbuffers support for Python",
    long_description_content_type="text/x-rst",
    version="23.1.0.b9",
    install_requires=[
        "attrs >= 23.1.0",
        "flatbuffers==23.1.4",
        "click",
        "lark >= 1.1.5",
        "immutables",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=ext_modules,
    zip_safe=False,
    extras_require={
        "dev": [
            "pytest",
            "hypothesis",
            "cython==0.29.32",
            "coverage",
            "cattrs",
            "nox",
            "numpy",
            "black==23.1.0",
            "isort",
        ]
    },
    package_data={"": ["*.pxd", "*.pyx", "py.typed"]},
    license="MIT license",
    entry_points={"console_scripts": ["flattrs=flattrs.modgen.__main__:main"]},
)
