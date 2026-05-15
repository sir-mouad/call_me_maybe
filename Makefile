install:
		UV_CACHE_DIR=/goinfre/mhadir/.cache_uv
		uv sync
run:
	uv run python -m src

debug:
	uv run python -m pdb -m src
	
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache	

lint:
	flake8 . --exclude .venv,__pycache__,llm_sdk
	mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs --exclude .venv,__pycache__,llm_sdk

lint-strict:
			flake8 . --exclude .venv,__pycache__,llm_sdk
			mypy . --strict --exclude '(\.venv|__pycache__|llm_sdk)'