.PHONY: help install run clean

help:
	@echo "Available commands:"
	@echo "  make install - Install dependencies"
	@echo "  make run     - Run the application"
	@echo "  make clean   - Clean cache files"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .ruff_cache

