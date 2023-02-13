WHEEL_DOCKER_IMAGE := quay.io/pypa/manylinux_2_28_x86_64

flatc:
	flatc -p -o flatc -I tests/flatbufferdefs/ tests/flatbufferdefs/*/*.fbs
	flatc -p -o flatc -I tests/flatbufferdefs/ tests/flatbufferdefs/*.fbs

flattrs:
	rm -rf tests/flattrs/models &&\
	python -m flattr.modgen tests/flatbufferdefs tests/flattrs/models &&\
	isort tests/flattrs/models &&\
	black tests/flattrs/models

coverage:
	coverage run --source=flattr -m pytest

wheels:
	rm -rf wheelhouse build &&\
	docker pull $(WHEEL_DOCKER_IMAGE) &&\
	docker run --rm -v `pwd`:/io $(WHEEL_DOCKER_IMAGE) /io/build-wheels.sh

compile:
	python setup.py build_ext --inplace