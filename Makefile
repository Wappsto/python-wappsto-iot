TEST_PATH=./test

.PHONY: clean-pyc clean-build build

clean: clean-pyc clean-build

clean-all: clean-pyc clean-build clean-env
	rm wappsto_iot_test.log

clean-pyc:
	find -name __pycache__ -exec rm -rf {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
	rm --force --recursive .tox
	rm --force --recursive htmlcov
	rm --force --recursive .coverage
	rm --force --recursive .mypy_cache
	rm --force --recursive .pytest_cache
	rm --force --recursive .cprofile

clean-env:
	rm --force pyvenv.cfg
	rm --force --recursive bin/
	rm --force --recursive lib/
	rm --force --recursive lib64
	rm --force --recursive share/
	rm --force --recursive include/

build: clean-pyc clean-build
	python3 setup.py sdist bdist_wheel

publish: build
	@echo "Please make sure that you have set 'TWINE_PASSWORD'."
	python3 -m twine upload -u seluxit --skip-existing dist/*

install: build
	pip3 install .

setup:
	pip3 install --user --requirement requirements.txt

