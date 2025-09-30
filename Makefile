# Simple helpers for building and uploading the package

.PHONY: build clean upload upload-test dist

build:
	python -m pip install --upgrade build twine
	python -m build

clean:
	rm -rf build dist *.egg-info src/*.egg-info

upload: build
	# Requires TWINE_PASSWORD (PyPI token) to be set; username is __token__
	TWINE_USERNAME=__token__ twine upload dist/*

upload-test: build
	# Requires TWINE_PASSWORD (TestPyPI token) to be set; username is __token__
	TWINE_USERNAME=__token__ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
