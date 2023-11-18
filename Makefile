ACTIVATE = . .venv/bin/activate

.venv:
	python3.9 -m venv .venv

virtualenv: .venv

pip: virtualenv
	@$(ACTIVATE) && pip install --upgrade pip pip-tools

reqs-prod: pip
	@$(ACTIVATE) && pip install --no-deps -r requirements.txt

reqs-dev: pip
	@$(ACTIVATE) && pip install --no-deps -r requirements-dev.txt

install: virtualenv reqs-prod

install-dev: virtualenv reqs-dev

lint: reqs-dev
	@$(ACTIVATE) && PYTHONPATH=. pylint rpi_remote_server

lock: pip
	@$(ACTIVATE) && pip-compile --generate-hashes --no-emit-index-url --output-file=requirements.txt \
		--resolver=backtracking pyproject.toml
	@$(ACTIVATE) && pip-compile --generate-hashes --no-emit-index-url --output-file=requirements-dev.txt \
		--resolver=backtracking --extra dev pyproject.toml

build:
	@$(ACTIVATE) && python -m build

publish:
	@$(ACTIVATE) && python -m twine upload dist/*