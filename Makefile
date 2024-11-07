.PHONY: fmt check test

fmt:
	poetry run ruff format .
	poetry run ruff check --fix .

check:
	poetry run ruff format --check .
	poetry run ruff check .
	poetry run mypy geohash_hilbert

test:
	PYTHONDEVMODE=1 poetry run pytest -vvv -s

cythonize:
	poetry run cythonize -i geohash_hilbert/*.pyx
	poetry run python -c "import geohash_hilbert as ghh; print(ghh._hilbert.CYTHON_AVAILABLE)"
