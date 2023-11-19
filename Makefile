ACTIVATE = . .venv/bin/activate

.venv:
	python3.9 -m venv .venv

virtualenv: .venv

pip: virtualenv
	@$(ACTIVATE) && pip install --upgrade pip

reqs-prod: pip
	@$(ACTIVATE) && pip install .

reqs-dev: pip
	@$(ACTIVATE) && pip install .[dev]

install: virtualenv reqs-prod

install-dev: virtualenv reqs-dev

lint:
	@$(ACTIVATE) && pylint rpi_remote/

build:
	@$(ACTIVATE) && python -m build

publish:
	@$(ACTIVATE) && python -m twine upload --skip-existing dist/*