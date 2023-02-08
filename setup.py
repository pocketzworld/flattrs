from platform import python_implementation

from setuptools import find_packages, setup

if python_implementation() != "PyPy":
    from Cython.Build import cythonize

    ext_modules = cythonize("src/flattr/cflattr/*.pyx", annotate=True)
else:
    ext_modules = []

setup(
    name="flattrs",
    long_description="Flatbuffers support for Python",
    long_description_content_type="text/x-rst",
    version="0.1.16",
    install_requires=[
        "attrs",
        "flatbuffers==23.1.4",
        "click",
        "lark >= 1.1.5",
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
            "isort",
        ]
    },
    package_data={"": ["*.pxd", "*.pyx", "py.typed"]},
    license="MIT license",
)
