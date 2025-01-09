default:
	make check
	make run

run:
	python main.py

check:
	make test
	make lint

lint:
	pylint *.py #tests/**/*.py

test:
	python -m unittest discover

install:
	pip install -r requirements.txt

mac_install:
	python -m pip install -U -r requirements.txt 

update:
	pip freeze > requirements.txt
