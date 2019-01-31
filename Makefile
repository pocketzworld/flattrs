WHEEL_DOCKER_IMAGE := quay.io/pypa/manylinux1_x86_64

fbs:
	flatc --python -o tests tests/flatbufferdefs/*/*.fbs
	flatc --python -o tests tests/flatbufferdefs/*.fbs

wheels:
	rm -rf wheelhouse build &&\
	docker pull $(WHEEL_DOCKER_IMAGE) &&\
	docker run --rm -v `pwd`:/io $(WHEEL_DOCKER_IMAGE) /io/build-wheels.sh