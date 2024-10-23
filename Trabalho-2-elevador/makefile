.ONESHELL:



PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip3


venv/bin/activate: requirements.txt	
	-python3 -m venv venv
	-chmod -x ./venv/bin/activate
	-. ./venv/bin/activate
	-$(PIP) install -r requirements.txt

venv: venv/bin/activate
	-. ./venv/bin/activate


runfile: venv
	$(PYTHON) src/$(f).py

reset:
	- rm -r -f venv
	- rm -r -f src/__pycache__

reset_values: venv
	- $(PYTHON) src/reset_elev.py

run: venv 
	-clear
	-$(PYTHON) src/main.py

list: venv
	-clear
	-$(PIP) list

.PHONY: run runfile reset

.DEFAULT_GOAL := run 
