.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
       target, help = match.groups()
        print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr doc/coverage
	rm -fr doc/tests.html


test: ## run tests on every Python version with tox
	tox

docs: ## generate Sphinx HTML documentation, including API docs
	pip install --upgrade-strategy only-if-needed pydoc-markdown
	rm -f docs/index.md
	rm -fr docs/devconfig
	pydocmd generate

servedocs: docs ## compile the docs watching for changes
	pydocmd serve

public: docs
	pydocmd build -d public
	cp -R doc/coverage public
	cp -R doc/tests.html public

release: dist ## package and upload a release
	pip install --upgrade-strategy only-if-needed twine
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install