UV = uv run

all: test

clean:
	rm -rf build dist
	find . -name '*.pyc' -exec rm \{\} \;

install:
	uv sync --dev
	cp .github/hooks/pre-push .git/hooks/pre-push
	chmod +x .git/hooks/pre-push

build: clean
	uv build

check-syntax-errors:
	$(UV) python -m compileall -q openfisca_tunisie_entreprises

check-style:
	$(UV) ruff check .

format-style:
	$(UV) ruff format .
	$(UV) ruff check --fix .

check-yaml:
	$(UV) yamllint openfisca_tunisie_entreprises/parameters
	$(UV) yamllint openfisca_tunisie_entreprises/tests

test:
	$(UV) pytest

.PHONY: all clean install build check-syntax-errors check-style format-style check-yaml test
