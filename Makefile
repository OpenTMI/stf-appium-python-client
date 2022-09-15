.PHONY: setup test package publish

setup:
	pip install .
	pip install .[dev]

test:
	pytest --cov-report xml:coverage.xml --cov stf_appium_client --junitxml=results.xml test/

package:
	python setup.py sdist
	python setup.py bdist_wheel

publish:
	pip install twine
	export PATH=$HOME/.local/bin:$PATH
	twine upload dist/*
