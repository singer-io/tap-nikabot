# tap-nikabot

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the 
[Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md) to retrieve 
[Nikabot](https://www.nikabot.com/) timesheeting data.

## Quickstart

Install the package

```
$ pip install .
```

Discover the streams

```
$ tap-nikabot -c config.json --discover > catalog.json
```

Run the tap (you will need to edit the catalog to add `"selected": true` to a stream's metadata)

```
$ tap-nikabot -c config.json --catalog catalog.json
```

## Development

A Makefile is provided to manage a virtual environment.

```
$ make init
```

Will setup a virtual environment in `.venv` and install the package and all (development and production) dependencies.
You can activate the environment with

```
# macOS / Linux
$ source .venv/bin/activate

# Windows
$ source .venv/Scripts/activate
```

And run the linter / autoformatter (provided by [black](https://black.readthedocs.io/en/stable/)) with

```
$ make lint
```

## Todo

- [ ] Run [singer-check-tap](https://github.com/singer-io/singer-tools#singer-check-tap) tool to validate

