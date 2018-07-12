PYTHONEXE=python3 -B
# DO NOT rename it to PYTHONPATH as it will lead to weird issues!
PYTHON_INCLUDEPATH=../src/:$(PYTHONPATH)
PYTESTARGS=
COVARGS=--cov=checklisting --cov-report=term-missing
# Once there will be more tests we might enable parallelism
#PYTESTARGS=-n 4

PYTHONTESTS=--env=fixtures_dir:${PWD}/fixtures/ src/

all: test

test: unit

unit: python


python:
	PYTHONPATH=$(PYTHON_INCLUDEPATH) $(PYTHONEXE) -mpytest  ${COVARGS} $(PYTESTARGS) $(PYTHONTESTS) 

.PHONY: all unit python
