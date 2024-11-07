.PHONY: fmt check test

fmt:
	poetry run ruff format .
	poetry run ruff check --fix .

check:
	poetry run ruff format --check .
	poetry run ruff check .
	# poetry run mypy geohash_hilbert

test:
	PYTHONDEVMODE=1 poetry run pytest -vvv -s
