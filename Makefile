PYPI_REPO=https://upload.pypi.org/legacy/
define DOCKERFILE
FROM python:3.9-alpine
#RUN python -m pip install twine==4.0.2
endef
export DOCKERFILE
BEETS_IMG=beets-websearch
BUILD_IMG=beets-websearch-build
DOCKER_OPTS=--rm -u `id -u`:`id -g` \
                -v "`pwd`:/work" -w /work \
                --entrypoint sh $(BUILD_IMG) -c
OPENAPI_FILE=openapi.yaml
#OPENAPI_GENERATOR_VERSION=131fd518fbfe894cfa23619ede96adab707630d9 # v7.7.0+patch
OPENAPI_GENERATOR_VERSION=24b70a9200dc8532900a2896154081995c29fa91


.PHONY: wheel
wheel: clean python-container
	docker run $(DOCKER_OPTS) 'python3 setup.py bdist_wheel'

.PHONY: validate-openapi
validate-openapi:
	@echo Validating the OpenAPI spec at $(OPENAPI_FILE)
	@docker run -t --rm --mount "type=bind,src=$(realpath $(OPENAPI_FILE)),dst=/openapi.yaml" \
		--entrypoint=sh \
		stoplight/spectral:6.11.1 \
		-c "set -ex; \
			echo 'extends: [\"spectral:oas\"]' > .spectral.yaml; \
			spectral lint /openapi.yaml"

.PHONY: generate
generate: PKG=beetsplug.websearch
generate: .openapi-generator ## Generate server stub
	rm -rf ./build/src-gen
	docker --debug run -ti --rm -v "`pwd`:/work" -w /work -u `id -u`:`id -g` openapitools/openapi-generator-cli:local-$(OPENAPI_GENERATOR_VERSION) generate -i $(OPENAPI_FILE) -g python-fastapi -o ./build/src-gen --package-name=$(PKG).gen -p sourceFolder= -p fastapiImplementationPackage=$(PKG).controller
	rm -rf ./beetsplug/websearch/gen
	cp -r ./build/src-gen/beetsplug/websearch/gen ./beetsplug/websearch/gen

.PHONY: test
test: beets-container
	# Run unit tests
	mkdir -p data/beets
	@docker run --rm -u `id -u`:`id -g` \
		-v "`pwd`:/plugin" -w /plugin \
		-v "`pwd`/data:/data" \
		--entrypoint sh $(BEETS_IMG) -c \
		'set -x; python -m unittest discover /plugin/tests'

.PHONY: test-e2e
test-e2e: beets-container
	# Run e2e tests
	mkdir -p data/beets
	@docker run --rm -u `id -u`:`id -g` -w /plugin \
                -v "`pwd`:/plugin" -w /plugin \
		-v "`pwd`/data:/data" \
		-v "`pwd`/example_beets_config.yaml:/data/beets/config.yaml" \
                $(BEETS_IMG) \
		sh -c 'set -x; bats -T tests/e2e'

.PHONY: beets-sh
beets-sh beets-websearch: beets-%: beets-container
	mkdir -p data/beets
	docker run -ti --rm -u `id -u`:`id -g` --network=host \
		-v "`pwd`:/plugin" \
		-v "`pwd`/data:/data" \
		-v "`pwd`/example_beets_config.yaml:/data/beets/config.yaml" \
		-v /run:/host/run \
		-e PULSE_SERVER=unix:/host/run/user/`id -u`/pulse/native \
		$(BEETS_IMG) $*

example-data:
	mkdir -p data/beets
	docker run -ti --rm -u `id -u`:`id -g` --network=host \
		-v "`pwd`/data:/data" \
		-v "`pwd`/example_beets_config.yaml:/data/beets/config.yaml" \
		$(BEETS_IMG) ytimport --url-file=https://raw.githubusercontent.com/mgoltzsche/beets-ytimport/main/tests/e2e/example-urls.txt

.PHONY: beets-container
beets-container: wheel
	docker build --rm -t $(BEETS_IMG) .

.PHONY: release
release: clean wheel
	docker run -e PYPI_USER -e PYPI_PASS -e PYPI_REPO=$(PYPI_REPO) \
		$(DOCKER_OPTS) \
		'python3 -m twine upload --repository-url "$$PYPI_REPO" -u "$$PYPI_USER" -p "$$PYPI_PASS" dist/*'

.PHONY: clean
clean:
	rm -rf build dist *.egg-info
	find . -name __pycache__ -exec rm -rf {} \; || true

.PHONY: clean-data
clean-data: clean
	rm -rf data

.PHONY: python-container
python-container:
	echo "$$DOCKERFILE" | docker build --rm -f - -t $(BUILD_IMG) .

.PHONY: .openapi-generator
.openapi-generator: build/openapi-generator
	cd build/openapi-generator && git checkout $(OPENAPI_GENERATOR_VERSION)
	docker build --force-rm -t openapitools/openapi-generator-cli:local-$(OPENAPI_GENERATOR_VERSION) build/openapi-generator

build/openapi-generator:
	git clone -c advice.detachedHead=0 https://github.com/mgoltzsche/openapi-generator.git build/openapi-generator

