PYTHON ?= python

get_python_version = $(word 2,$(subst ., ,$(shell $(1) --version 2>&1)))
ifneq ($(call get_python_version,$(PYTHON)), 3)
	PYTHON = python3
endif
ifneq ($(call get_python_version,$(PYTHON)), 3)
	$(error "No supported python found! Requires python v3.6+")
endif

init:
	pip install -e .[dev]

discover:
	tap-nikabot -c config.json --discover

sync:
	tap-nikabot -c config.json --catalog catalog.json

lint-ci:
	pylint tap_nikabot tests *.py; \
	mypy --strict tap_nikabot

test-ci:
	coverage run -m pytest; \
	coverage report

lint:
	black -l 120 tap_nikabot tests *.py; \
	isort -rc tap_nikabot tests *.py; \
	pylint --exit-zero tap_nikabot tests *.py; \
	mypy --strict tap_nikabot || true

test: lint
	coverage run -m pytest; \
	coverage report

build: test
	rm -rf dist
	python setup.py sdist

deploy: build
	twine upload dist/*

deploy-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	rm -rf .venv .pytest_cache .mypy_cache dist *.egg-info
	find . -iname "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

.PHONY: init discover sync lint-ci test-ci lint test build deploy deploy-test clean
.SILENT:
