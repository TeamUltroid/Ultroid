test:
	@pre-commit run --all-files

install:
	@pip3 install --upgrade pip setuptools wheel
	@pip3 install --upgrade -r requirements.txt


dev-install:
	@pip3 install --upgrade pip setuptools wheel
	@pip3 install --upgrade -r requirements-dev.txt
	@sleep 5
	@pre-commit
	@pre-commit install

update:
	@git pull
	@pip3 install --upgrade pip setuptools wheel
	@pip3 install --upgrade -r requirements.txt

ci:
	@pip3 install --upgrade pip setuptools wheel
	@pip3 install --upgrade -r requirements-dev.txt
	@pre-commit
