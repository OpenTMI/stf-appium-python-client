.PHONY: setup test package publish

setup:
	pip install .
	pip install .[dev]

test:
	nosetests --with-xunit --with-coverage --cover-package=stf_appium_client --cover-html --cover-html-dir=htmlcov --cover-xml-file=coverage.xml --xunit-file=results.xml

package:
	python setup.py sdist
	python setup.py bdist_wheel

publish:
	pip install twine
	export PATH=$HOME/.local/bin:$PATH
	twine upload dist/*
