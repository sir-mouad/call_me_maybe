install:
		uv sync
run:
	time uv run python -m src

debug:
	uv run python -m pdb -m src
	
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache	


lint:
	flake8 . --exclude .venv,__pycache__,llm_sdk
	mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs --explicit-package-bases \
	--exclude '(\.venv|__pycache__|llm_sdk)'


lint-strict:
	flake8 . --exclude .venv,__pycache__,llm_sdk
	mypy . --strict --explicit-package-bases \
	--exclude '(\.venv|__pycache__|llm_sdk)'