.PHONY: vendor-sync install install-dev init lint license-headers test ci

vendor-sync:
	./scripts/vendor_sync.sh

install: vendor-sync
	pip install -e .
	pip install -e vendor/MetaGPT

install-dev: install
	pip install -e ".[dev]"

init:
	msc init

lint:
	ruff check packages scripts tests
	ruff format --check packages scripts tests

license-headers:
	python scripts/license_header.py --check

test:
	pytest -q

ci: lint license-headers test
	@test ! -d vendor/agency-agents/info-sentry || (echo "info-sentry must not be vendored" && exit 1)
	@test -f vendor/MetaGPT/LICENSE
	@test -f vendor/agency-agents/LICENSE
