# Simple helpers for building and uploading the package

.PHONY: build clean upload upload-test dist

build:
	python -m pip install --upgrade build twine
	python -m build

clean:
	rm -rf build dist *.egg-info src/*.egg-info

upload: build
	 twine upload --repository deepwiki_to_md dist/*

upload-test: build
	# Requires TWINE_PASSWORD (TestPyPI token) to be set; username is __token__
    twine upload --repository testpypi dist/*