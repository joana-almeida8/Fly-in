PIP_INSTALL = venv/bin/pip install
PYTHON = venv/bin/python

RM = rm -rf

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

.PHONY: install run debug clean lint lint-strict destroy

install:
	@echo "Creating virtual environment and installing dependencies..."
	python3 -m venv venv
	$(PIP_INSTALL) --upgrade pip
	$(PIP_INSTALL) pydantic pygame-ce flake8 mypy

run:
	@input=$$(bash scripts/pick_input.sh); \
	$(PYTHON) fly_in.py "$$input"

debug:
	@input=$$(bash scripts/pick_input.sh); \
	$(PYTHON) -m pdb fly_in.py "$$input"

clean:
	@echo "Cleaning cache files..."
	$(RM) __pycache__ src/__pycache__ src/*/__pycache__ .mypy_cache

lint:
	@echo "=== Running Linters ==="
	$(PYTHON) -m flake8 fly_in.py src/
	$(PYTHON) -m mypy fly_in.py  src/ $(MYPY_FLAGS)

lint-strict:
	@echo "=== Running Strict Linters ==="
	$(PYTHON) -m flake8 fly_in.py src/
	$(PYTHON) -m mypy --strict fly_in.py src/

destroy: clean
	@echo "Destroying virtual environment..."
	$(RM) venv