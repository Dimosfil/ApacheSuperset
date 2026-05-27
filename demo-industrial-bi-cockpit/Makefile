.PHONY: help env config seed-local test-ai

help:
	@echo "Industrial BI Cockpit demo"
	@echo "  make env         Create .env from .env.example if missing"
	@echo "  make config      Validate docker compose configuration"
	@echo "  make seed-local  Run optional Python reseed script against local Postgres"
	@echo "  make test-ai     Run AI chart assistant regression tests"

env:
	@if not exist .env copy .env.example .env

config:
	docker compose config

seed-local:
	python -m pip install -r db/requirements.txt
	python db/seed.py

test-ai:
	python -m unittest discover -s ai-chart-assistant/tests -v
