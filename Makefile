.PHONY: verify build serve

# Everything CI does, plus syntax checks. Writes .claude/.last-verify-passed on success.
verify:
	uv sync --locked
	uv run python -m compileall -q pixelhome homes
	node --check site/app.js
	uv run python -m pixelhome build --out dist
	scripts/verify-sentinel.sh

build:
	uv run python -m pixelhome build --out dist

serve: build
	python3 -m http.server -d dist 8000
