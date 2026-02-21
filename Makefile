DOCKER="docker"
IMAGE_NAME="kiansheik/nhe-enga"
TAG_NAME="production"

REPOSITORY=""
FULL_IMAGE_NAME=${IMAGE_NAME}:${TAG_NAME}

lint:
	black .

push:
	make lint
	make test
	git add .
	git commit
	git push origin HEAD

test:
	python3 tests/run_tests.py $(ARGS)
