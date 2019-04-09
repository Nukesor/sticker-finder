.PHONY: default
default: install

.PHONY: install
install:
	poetry install --develop .

.PHONY: run
run:
	poetry run python main.py
