TEST_PATH=./test
PY_VERSION=python3.10
PY_ENV=env

.PHONY: clean-pyc clean-build build

clean: clean-pyc clean-build

clean-all: clean-pyc clean-build clean-env
	rm --force wappsto_iot_test.log

clean-pyc:
	find -name __pycache__ -exec rm -rf {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
	rm --force --recursive .tox
	rm --force --recursive htmlcov
	rm --force --recursive coverage.json
	rm --force --recursive .coverage
	rm --force --recursive .mypy_cache
	rm --force --recursive .pytest_cache
	rm --force --recursive .cprofile

clean-env:
	rm --force --recursive ${PY_ENV}/

lint:
	${PY_ENV}/bin/flake8 --docstring-convention google --ignore D212,W503  wappstoiot/*.py wappstoiot/**/*.py
	${PY_ENV}/bin/mypy --strict --follow-imports=normal --python-version 3.7  wappstoiot/*.py wappstoiot/**/*.py

test: lint
	${PY_ENV}/bin/tox

gen-stub:
	${PY_ENV}/bin/stubgen wappstoiot/{*,**/*}.py --out .

build: clean-pyc clean-build
	${PY_ENV}/bin/pip install wheel twine
	${PY_ENV}/bin/python3 setup.py sdist bdist_wheel

publish: build test
	@echo "Please make sure that you have set 'TWINE_PASSWORD'."
	${PY_ENV}/bin/python3 -m twine upload -u seluxit --skip-existing dist/*

install:
	pip3 install .

setup:
	${PY_VERSION} -m venv ${PY_ENV}/.
	${PY_ENV}/bin/pip3 install --upgrade pip
	${PY_ENV}/bin/pip3 install --requirement requirements.txt

