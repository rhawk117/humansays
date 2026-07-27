.PHONY: format lint test ci

format:
	@bash scripts/format.sh

lint:
	@bash scripts/lint.sh

test:
	@bash scripts/test.sh

ci:
	@bash scripts/ci.sh

.DEFAULT_GOAL := ci
