.PHONY: format lint ci

format:
	@bash scripts/format.sh

lint:
	@bash scripts/lint.sh

ci:
	@bash scripts/ci.sh

.DEFAULT_GOAL := ci
