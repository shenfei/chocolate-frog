VENV = venv
PYTHON = $(VENV)/bin/python

PIP = $(VENV)/bin/pip

# `w` stands for `wipe`
PIP_INSTALL = $(PIP) install --exists-action=w

# dependency setup
setup: venv deps

deps:
	@$(PIP_INSTALL) -r requirements.txt

venv:
	@virtualenv $(VENV) --prompt '<venv:chocolate>'
	@$(PIP_INSTALL) -i $(PIP_MIRROR) -U pip setuptools

clean_pyc:
	@find . -not \( -path './venv' -prune \) -name '*.pyc' -exec rm -f {} \;
