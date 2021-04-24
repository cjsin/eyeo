PACKAGE_NAME := eyeo
ACTIVATE     := source venv/bin/activate
VERSION      := $(shell tr -d ' ' < setup.cfg | awk -F= '/^version=/ {print $$2}')
DISTWHEEL    := $(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl
README       := README.md

all: build

version:
	@echo Package: $(PACKAGE_NAME)
	@echo Version: $(VERSION)
	@echo Wheel: $(DISTWHEEL)

lint:
	pylint-3 src

doc: $(README)
	pdoc $(PACKAGE_NAME) > $(README)

build-reqs:
	pip list | egrep '^build[[:space:]]' || python3 -m pip install --upgrade build

build: build-reqs
	python3 -m build

clean:
	rm -rf venv build dist src/__pycache__ .pytest_cache

%.whl: build
	cp dist/$@ ./

clean-venv:
	rm -rf ./venv

venv:
	python3 -m venv venv

venv-install: venv $(DISTWHEEL)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install --force-reinstall $(DISTWHEEL)

venv-run-examples: venv-install
	$(ACTIVATE) && python3 -m eyeo.examples
	$(ACTIVATE) && python3 -m eyeo.stringify_examples

venv-test: clean-venv venv-run-examples

test:
	PYTHONPATH=$(PWD)/src python3 -m eyeo.examples
	PYTHONPATH=$(PWD)/src python3 -m eyeo.stringify_examples
