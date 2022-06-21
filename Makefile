WHEEL_DOCKER_IMAGE := quay.io/pypa/manylinux_2_28_x86_64

fbs:
	flatc --python -o tests tests/flatbufferdefs/*/*.fbs
	flatc --python -o tests tests/flatbufferdefs/*.fbs

coverage:
	coverage run --source=flattr -m pytest

wheels:
	rm -rf wheelhouse build &&\
	docker pull $(WHEEL_DOCKER_IMAGE) &&\
	docker run --rm -v `pwd`:/io $(WHEEL_DOCKER_IMAGE) /io/build-wheels.sh