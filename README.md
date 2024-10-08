# beets-websearch

A [beets](https://github.com/beetbox/beets) plugin to search tracks and save the result as playlists via HTTP.

## Features

* Provides a JSON REST API to search tracks.
* Allows to save searches as playlists.

## Installation

```sh
python3 -m pip install beets-websearch
```

## Configuration

Enable the plugin and add a `websearch` section to your beets `config.yaml` as follows:
```yaml
plugins:
  - websearch

websearch
  host: '127.0.0.1'
  port: 5000
```

## Usage

Once the `websearch` plugin is enabled within your beets configuration, you can run it as follows:
```sh
beet websearch
```

You can browse the server at [`http://127.0.0.1:5000`](http://127.0.0.1:5000).

To serve multiple beets web APIs using a single process, you can use the [webrouter plugin](https://github.com/mgoltzsche/beets-webrouter).

### CLI

```
Usage: beet websearch [options]

Options:
  -h, --help   show this help message and exit
  -d, --debug  debug mode
```

## Web API

See [OpenAPI definition](./openapi.yaml).

## Development

The following assumes you have [docker](https://docs.docker.com/engine/install/) installed.

In case you make changes to the [`openapi.yaml`](./openapi.yaml), you can validate them as follows:
```sh
make validate-openapi
```

Generate the server stub from the [openapi.yaml](./openapi.yaml) (containerized):
```sh
make generate
```

Run the unit tests (containerized):
```sh
make test
```

Run the e2e tests (containerized):
```sh
make test-e2e
```

To test your plugin changes manually, you can run a shell within a beets docker container as follows:
```sh
make beets-sh
```

A temporary beets library is written to `./data`.
It can be removed by calling `make clean-data`.

To download example data, run:
```sh
make example-data
```

To just start the server, run:
```sh
make beets-websearch
```

Now you can browse the executable API documentation at [`http://127.0.0.1:5000/docs`](http://127.0.0.1:5000/docs).

Example API call to search tracks: [`http://127.0.0.1:5000/tracks?query={%22artist%22:{%22contains%22:%20%22dengue%22},%22title%22:{%22contains%22:%22serpiente%22}}`](http://127.0.0.1:5000/tracks?query={%22artist%22:{%22contains%22:%20%22dengue%22},%22title%22:{%22contains%22:%22serpiente%22}}).
