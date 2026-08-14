# Local development helpers. Install the dev extra before running these targets.

.PHONY: build clean format format-check lint type-check check

build:
	python -m build

clean:
	rm -rf build dist .pytest_tmp .coverage htmlcov coverage.xml *.egg-info src/*.egg-info

format:
	python -m black src wiki_tests
	python -m isort src wiki_tests

format-check:
	python -m black --check src tests wiki_tests
	python -m isort --check-only src tests wiki_tests

lint:
	python -m flake8 src tests wiki_tests

type-check:
	python -m mypy src

check: format-check lint type-check
	python -m pytest
