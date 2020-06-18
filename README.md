# tap-nikabot

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md) to retrieve [Nikabot](https://www.nikabot.com/) timesheeting data.

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

See the [Singer documentation](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md) for full usage.

## Development

A Makefile is provided to manage a virtual environment.

```
$ make init
```

Will setup a [virtual environment](https://docs.python.org/3/tutorial/venv.html) in `.venv` and install the package and all (development and production) dependencies.

To run the linter / autoformatter (provided by [black](https://black.readthedocs.io/en/stable/)) 

```
$ make lint
```

To run the test suite (which also runs the linter)

```
$ make test
```

To run the tap in discovery mode (loads config from `config.json`)

```
$ make discover
```

Or to run it in sync mode (loads catalog from `catalog.json` and config from `config.json`)

```
$ make sync
```

### Proxying requests

You can proxy all requests through a proxy tool like OWASP ZAP, BurpSuite, Fiddler or Charles Proxy using environment variables to control the [python requests pacakge](https://requests.readthedocs.io/en/master/user/advanced/#proxies). And easy way to manage this is with a shell script that sets environment variables. Create the script `env.sh`:

```
#!/bin/sh
##
# Script to execute a command with specific environment variables set.
# Note that environment variables passed as arguments will need to be escaped to avoid shell expansion.
#
# USAGE:
#   ./env.sh my-command
#   ./env.sh 'echo $MY_VAR'
##

set -e

export HTTP_PROXY="http://localhost:8080"
export HTTPS_PROXY="http://localhost:8080"
export REQUESTS_CA_BUNDLE="C:\path\to\owasp_zap_root_ca.cer"

eval "$@"
```

Update REQUESTS_CA_BUNDLE to point to the CA certificate for the proxy tool. Now pass your command to the script to run it.

```
$ ./env.sh make discover > catalog.json
$ ./env.sh tap-nikabot -c config.json --catalog catalog.json
```

## Todo

- [ ] Run [singer-check-tap](https://github.com/singer-io/singer-tools#singer-check-tap) tool to validate

