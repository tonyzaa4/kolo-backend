.PHONY: setup

setup:
	alembic upgrade head
	python seed.py
