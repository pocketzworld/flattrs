#!/bin/bash
set -e -x

# Compile wheels
for PYBIN in /opt/python/cp3{5,6,7,8}*/bin; do
    "${PYBIN}/pip" install /io/
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/flattrs*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done
