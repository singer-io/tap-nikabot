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

lint:
	source $(VENV_ACTIVATE); \
		black -l 120 tap_nikabot tests *.py; \
		pylint --exit-zero tap_nikabot tests *.py

test: lint
	source $(VENV_ACTIVATE); \
        coverage run --source=tap_nikabot -m pytest; \
		coverage report --skip-covered

db:
	docker run -e POSTGRES_PASSWORD=stitches -p 5432:5432 --rm postgres

.PHONY: init lint test db
.SILENT:
