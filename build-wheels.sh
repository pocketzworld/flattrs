#!/bin/bash
set -e -x

# Compile wheels
for PYBIN in /opt/python/cp3{10,11,12,13}*/bin/; do
    # Directories ending with 't' are free-threaded builds which Cython doesn't
    # support yet, so we skip them.
    [[ $PYBIN == *t/bin/ ]] && continue
    "${PYBIN}/pip" install /io/
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/flattrs*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done
