.PHONY: test


test:
	nosetests --with-xunit --with-coverage --cover-package=stf_appium_client --cover-html --cover-html-dir=htmlcov --cover-xml-file=coverage.xml --xunit-file=results.xml
