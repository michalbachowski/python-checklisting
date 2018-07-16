

clean:
	rm -rf build
	rm -rf .coverage\.*
	rm -rf .pytest_cache
	find . -name __pycache__ -exec rm -rf {} \;
	find ./src -not -name checklisting -maxdepth 1 -mindepth 1 -exec rm -rf {} \;

zipapp:
	pip install -r {toxinidir}/requirements.txt --target src/
	python -mzipapp {toxinidir}/src -o {toxinidir}/dist/checklisting.pyz -p '/usr/bin/env python3' -m 'checklisting.cli:main'

sdist:
	python setup.py clean --all sdist bdist_wheel

.PHONY: clean zipapp sdist
