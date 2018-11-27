clean:
	rm -rf build
	rm -rf .coverage\.*
	rm -rf .pytest_cache
	find . -name __pycache__i -o -name '*.pyc' -depth -exec rm -rf {} \;
	find ./src -not -name checklisting -maxdepth 1 -mindepth 1 -exec rm -rf {} \;

zipapp:
	pip install -r {toxinidir}/requirements.txt --target src/
	python -mzipapp {toxinidir}/src -o {toxinidir}/dist/checklisting.pyz -p '/usr/bin/env python3' -m 'checklisting.cli:main'

sdist:
	python setup.py clean --all sdist bdist_wheel

webserver:
	PYTHONPATH=src/:$(PYTHONPATH) python3 -mchecklisting webserver --config=tests/fixtures/sample_checklists/simple_config.yml

cli:
	PYTHONPATH=src/:$(PYTHONPATH) python3 -mchecklisting cli --config=tests/fixtures/sample_checklists/simple_config.yml

call_local:
	PYTHONPATH=src/:$(PYTHONPATH) python3 -mchecklisting external -s http://127.0.0.1:8080

tests:
	$(shell cat .env) python3 -B -mpytest --cov=checklisting --cov-report=term-missing tests/src/

.PHONY: clean zipapp sdist cli server server tests
