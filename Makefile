PIP_INSTALL = venv/bin/pip install
PYTHON = venv/bin/python

RM = rm -rf

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

.PHONY: install run debug clean lint lint-strict destroy

install:
	python3 -m venv venv
	$(PIP_INSTALL) --upgrade pip
	$(PIP_INSTALL) pydantic
	$(PIP_INSTALL) pygame-ce
	$(PIP_INSTALL) flake8
	$(PIP_INSTALL) mypy

run:
	$(PYTHON) fly_in.py config.txt

debug:
	$(PYTHON) -m pdb fly_in.py config.txt

clean:
	$(RM) __pycache__
	$(RM) src/parse/__pycache__
	$(RM) .mypy_cache

lint:
	$(PYTHON) -m flake8 fly_in.py
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy fly_in.py $(MYPY_FLAGS)
	$(PYTHON) -m mypy src $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 fly_in.py
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy --strict fly_in.py
	$(PYTHON) -m mypy --strict src

destroy: clean
	$(RM) venv