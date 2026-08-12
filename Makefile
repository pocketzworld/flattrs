.PHONY: flatc flattrs wheels wheels-manylinux wheels-musllinux

MANYLINUX_DOCKER_IMAGE := quay.io/pypa/manylinux_2_28_x86_64
MUSLLINUX_DOCKER_IMAGE := quay.io/pypa/musllinux_1_2_x86_64

flatc:
	flatc -p -o flatc -I tests/flatbufferdefs/ tests/flatbufferdefs/*/*.fbs
	flatc -p -o flatc -I tests/flatbufferdefs/ tests/flatbufferdefs/*.fbs

flattrs:
	rm -rf tests/flattrs/models &&\
	python -m flattrs.modgen --gen-namespace-exports tests/flatbufferdefs tests/flattrs/models &&\
	isort tests/flattrs/models &&\
	black tests/flattrs/models

coverage:
	coverage run --source=flattrs -m pytest

# Both are needed: manylinux for glibc images, musllinux for alpine. An alpine
# image with no musllinux wheel silently falls back to the pure-Python
# flatbuffers builder, which rejects values the compiled one coerces.
wheels: wheels-manylinux wheels-musllinux

wheels-manylinux:
	rm -rf wheelhouse build &&\
	docker pull $(MANYLINUX_DOCKER_IMAGE) &&\
	docker run --rm -v `pwd`:/io $(MANYLINUX_DOCKER_IMAGE) /io/build-wheels.sh

wheels-musllinux:
	rm -rf build &&\
	docker pull $(MUSLLINUX_DOCKER_IMAGE) &&\
	docker run --rm -v `pwd`:/io $(MUSLLINUX_DOCKER_IMAGE) /io/build-wheels.sh

compile:
	python setup.py build_ext --inplace