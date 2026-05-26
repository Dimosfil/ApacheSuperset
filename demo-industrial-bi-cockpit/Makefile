.PHONY: help env config seed-local

help:
	@echo "Industrial BI Cockpit demo"
	@echo "  make env         Create .env from .env.example if missing"
	@echo "  make config      Validate docker compose configuration"
	@echo "  make seed-local  Run optional Python reseed script against local Postgres"

env:
	@if not exist .env copy .env.example .env

config:
	docker compose config

seed-local:
	python -m pip install -r db/requirements.txt
	python db/seed.py
