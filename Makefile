SHELL := /bin/bash
VENV := .venv
PIP := $(VENV)/bin/pip
REQ_MAIN := requirements.txt
REQ_DEV := requirements.dev.txt
DEPS_STAMP := $(VENV)/.deps-stamp

.DEFAULT_GOAL := ready

.PHONY: install venv pip-upgrade format format-check lint lint-fix typecheck test security fix check ready clean

$(DEPS_STAMP): $(REQ_MAIN) $(REQ_DEV)
	@echo "⟩ creating virtualenv"
	python3 -m venv $(VENV)
	@echo "⟩ upgrading pip"
	$(PIP) install --upgrade pip
	@if [ -s $(REQ_MAIN) ]; then \
		echo "⟩ installing runtime requirements"; \
		$(PIP) install -r $(REQ_MAIN); \
	fi
	@echo "⟩ installing dev requirements"
	$(PIP) install -r $(REQ_DEV)
	@touch $@

install: $(DEPS_STAMP)
venv: install

pip-upgrade: install
	$(PIP) install --upgrade pip

format: install
	$(VENV)/bin/ruff format .

format-check: install
	$(VENV)/bin/ruff format --check .

lint: install
	$(VENV)/bin/ruff check .

lint-fix: install
	$(VENV)/bin/ruff check --fix .

typecheck: install
	$(VENV)/bin/pyright

test: install
	$(VENV)/bin/pytest

security: install
	$(VENV)/bin/bandit -q -r donk

fix:
	$(MAKE) format
	$(MAKE) lint-fix

check:
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) security
	$(MAKE) test

ready:
	$(MAKE) fix
	$(MAKE) check

clean:
	rm -rf $(VENV)
