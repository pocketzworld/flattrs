.PHONY: flatc flattrs wheels wheels-all wheels-x86_64 wheels-aarch64 \
	wheels-manylinux wheels-musllinux

# Cross-building a foreign arch needs binfmt/QEMU on the host:
#   docker run --rm --privileged tonistiigi/binfmt --install all
ARCH ?= x86_64

ifeq ($(ARCH),aarch64)
DOCKER_PLATFORM := linux/arm64
else
DOCKER_PLATFORM := linux/amd64
endif

MANYLINUX_DOCKER_IMAGE := quay.io/pypa/manylinux_2_28_$(ARCH)
MUSLLINUX_DOCKER_IMAGE := quay.io/pypa/musllinux_1_2_$(ARCH)

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

wheels-all: wheels-x86_64 wheels-aarch64

wheels-x86_64:
	$(MAKE) wheels ARCH=x86_64

wheels-aarch64:
	$(MAKE) wheels ARCH=aarch64

wheels-manylinux:
	rm -rf build &&\
	docker pull --platform $(DOCKER_PLATFORM) $(MANYLINUX_DOCKER_IMAGE) &&\
	docker run --rm --platform $(DOCKER_PLATFORM) -v `pwd`:/io $(MANYLINUX_DOCKER_IMAGE) /io/build-wheels.sh

wheels-musllinux:
	rm -rf build &&\
	docker pull --platform $(DOCKER_PLATFORM) $(MUSLLINUX_DOCKER_IMAGE) &&\
	docker run --rm --platform $(DOCKER_PLATFORM) -v `pwd`:/io $(MUSLLINUX_DOCKER_IMAGE) /io/build-wheels.sh

compile:
	python setup.py build_ext --inplace
