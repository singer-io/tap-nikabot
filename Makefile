VENV_NAME ?= .venv
PYTHON ?= python

get_python_version = $(word 2,$(subst ., ,$(shell $(1) --version 2>&1)))
ifneq ($(call get_python_version,$(PYTHON)), 3)
	PYTHON = python3
endif
ifneq ($(call get_python_version,$(PYTHON)), 3)
	$(error "No supported python found! Requires python v3.6+")
endif

ifdef OS
	VENV_ACTIVATE ?= $(VENV_NAME)/Scripts/activate
else
	VENV_ACTIVATE ?= $(VENV_NAME)/bin/activate
endif

init:
	test -d $(VENV_NAME) || $(PYTHON) -m venv $(VENV_NAME)
	source $(VENV_ACTIVATE); \
		pip install -q -r requirements.txt; \
		pip install -e .

discover:
	source $(VENV_ACTIVATE); \
	    tap-nikabot -c config.json --discover

sync:
	source $(VENV_ACTIVATE); \
	    tap-nikabot -c config.json --catalog catalog.json

lint:
	black -l 120 tap_nikabot tests *.py; \
	flake8 --exit-zero tap_nikabot tests *.py; \
	mypy --strict tap_nikabot; \
	pylint tap_nikabot --disable 'broad-except,chained-comparison,empty-docstring,fixme,invalid-name,line-too-long,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-else-raise,no-else-return,too-few-public-methods,too-many-arguments,too-many-branches,too-many-lines,too-many-locals,ungrouped-imports,wrong-spelling-in-comment,wrong-spelling-in-docstring,bad-whitespace' || true

test: lint
	coverage run -m pytest; \
		coverage report

build: test
	rm -rf dist
	source $(VENV_ACTIVATE); \
	python setup.py sdist

deploy: build
	twine upload dist/*

deploy-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

db:
	docker run -e POSTGRES_PASSWORD=stitches -p 5432:5432 --rm postgres

.PHONY: init discover sync lint test build deploy deploy-test db
.SILENT:
