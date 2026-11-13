PY ?= python3
export PYTHONPATH := src:examples

reproduce:
	$(PY) examples/reproduce_icdm.py
	$(PY) examples/reproduce_sgof.py

test:
	$(PY) -m pytest -q tests

.PHONY: reproduce test
